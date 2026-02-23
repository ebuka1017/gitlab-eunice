"""gitlab api client for eunice - real data extraction with rate limiting"""
import gitlab
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time


class EuniceGitLabClient:
    """wrapper around python-gitlab with eunice-specific methods"""
    
    def __init__(self, url: str, token: str):
        self.gl = gitlab.Gitlab(url, private_token=token)
        self.rate_limit_window = []
        
    def get_file_commits(self, project_id: str, file_path: str, since_days: int = 30) -> List:
        """
        get commits touching a specific file
        
        reality check: paginated, rate limited
        """
        project = self.gl.projects.get(project_id)
        since = datetime.now() - timedelta(days=since_days)
        
        commits = []
        page = 1
        
        while True:
            self._check_rate_limit()
            
            batch = project.commits.list(
                path=file_path,
                since=since.isoformat(),
                page=page,
                per_page=100  # max allowed
            )
            
            if not batch:
                break
                
            commits.extend(batch)
            page += 1
            
            # gitlab pagination limit
            if page > 100:
                break
        
        return commits
    
    def get_mrs_with_file_changes(
        self, 
        project_id: str, 
        file_path: str, 
        since_days: int = 30
    ) -> List:
        """
        get merge requests that modified a file
        
        reality check: use commit → mr mapping, not looping all mrs
        """
        # get commits for file first (already limited to time window)
        commits = self.get_file_commits(project_id, file_path, since_days)
        
        if not commits:
            return []
        
        project = self.gl.projects.get(project_id)
        mrs = set()
        
        for commit in commits:
            self._check_rate_limit()
            
            try:
                # gitlab can map commit → mr
                commit_obj = project.commits.get(commit.id)
                commit_mrs = commit_obj.merge_requests()
                
                for mr in commit_mrs:
                    if mr.state == 'merged':
                        mrs.add(mr.iid)
            except Exception as e:
                # fallback: skip this commit
                continue
        
        # fetch full mr objects
        full_mrs = []
        for mr_iid in mrs:
            self._check_rate_limit()
            try:
                mr = project.mergerequests.get(mr_iid)
                full_mrs.append(mr)
            except:
                continue
        
        return full_mrs
    
    def calculate_mr_review_time(self, mr) -> Optional[float]:
        """
        calculate time from creation to merge in minutes
        
        reality check: handle timezone-aware datetimes
        """
        if not mr.merged_at:
            return None
        
        try:
            created = datetime.fromisoformat(mr.created_at.replace('Z', '+00:00'))
            merged = datetime.fromisoformat(mr.merged_at.replace('Z', '+00:00'))
            return (merged - created).total_seconds() / 60
        except:
            return None
    
    def get_bug_issues_with_time_tracking(
        self, 
        project_id: str, 
        file_path: str,
        since_days: int = 30
    ) -> List[Dict]:
        """
        get bug issues mentioning file with time spent
        
        reality check: time_stats.total_time_spent is in SECONDS
        """
        project = self.gl.projects.get(project_id)
        
        self._check_rate_limit()
        
        updated_after = (datetime.now() - timedelta(days=since_days)).isoformat()
        issues = project.issues.list(
            labels=['bug'],
            search=file_path,
            updated_after=updated_after,
            all=True
        )
        
        issues_with_time = []
        for issue in issues:
            time_stats = getattr(issue, 'time_stats', {})
            total_time_spent = time_stats.get('total_time_spent', 0)
            
            if total_time_spent and total_time_spent > 0:
                # convert seconds to hours
                hours = total_time_spent / 3600
                issues_with_time.append({
                    'issue': issue,
                    'issue_id': issue.iid,
                    'hours_spent': hours,
                    'title': issue.title,
                    'web_url': issue.web_url
                })
        
        return issues_with_time
    
    def get_pipelines_touching_file(
        self, 
        project_id: str, 
        file_path: str, 
        since_days: int = 30
    ) -> List:
        """
        get pipelines that changed a file
        
        reality check: use commit → pipeline mapping
        """
        # get commits for file
        commits = self.get_file_commits(project_id, file_path, since_days)
        
        if not commits:
            return []
        
        project = self.gl.projects.get(project_id)
        pipelines = {}  # deduplicate by id
        
        for commit in commits:
            self._check_rate_limit()
            
            try:
                # get pipelines for this commit sha
                commit_pipelines = project.pipelines.list(sha=commit.id)
                
                for pipeline in commit_pipelines:
                    pipelines[pipeline.id] = pipeline
            except:
                continue
        
        return list(pipelines.values())
    
    def calculate_pipeline_stats(self, pipelines: List) -> Dict:
        """calculate aggregate pipeline statistics"""
        if not pipelines:
            return {
                'avg_duration_minutes': 0,
                'failure_rate': 0,
                'failed_count': 0,
                'total_count': 0
            }
        
        total_duration = 0
        failed_count = 0
        
        for pipeline in pipelines:
            if hasattr(pipeline, 'duration') and pipeline.duration:
                total_duration += pipeline.duration
            
            if pipeline.status in ['failed', 'canceled']:
                failed_count += 1
        
        avg_duration = (total_duration / len(pipelines)) / 60  # convert to minutes
        failure_rate = failed_count / len(pipelines) if pipelines else 0
        
        return {
            'avg_duration_minutes': round(avg_duration, 2),
            'failure_rate': round(failure_rate, 3),
            'failed_count': failed_count,
            'total_count': len(pipelines),
            'pipeline_ids': [p.id for p in pipelines]
        }
    
    def get_file_complexity_from_code_quality(
        self, 
        project_id: str, 
        mr_id: int
    ) -> Optional[Dict]:
        """
        get code quality metrics from ci artifacts
        
        reality check: not a simple rest endpoint, parse from artifacts
        """
        try:
            project = self.gl.projects.get(project_id)
            mr = project.mergerequests.get(mr_id)
            
            # get pipeline for mr
            if not hasattr(mr, 'head_pipeline') or not mr.head_pipeline:
                return None
            
            pipeline = project.pipelines.get(mr.head_pipeline['id'])
            
            # find code_quality job
            jobs = pipeline.jobs.list(all=True)
            code_quality_job = None
            
            for job in jobs:
                if 'code_quality' in job.name.lower() or 'codeclimate' in job.name.lower():
                    code_quality_job = job
                    break
            
            if not code_quality_job:
                return None
            
            # for now, return placeholder
            # actual implementation would parse artifact json
            return {
                'complexity_available': False,
                'note': 'code quality parsing from artifacts not yet implemented'
            }
            
        except Exception as e:
            return None
    
    def _check_rate_limit(self):
        """
        respect gitlab rate limits
        gitlab.com: 2000 requests/minute for authenticated users
        """
        now = datetime.now()
        
        # remove requests older than 1 minute
        self.rate_limit_window = [
            req for req in self.rate_limit_window 
            if (now - req).seconds < 60
        ]
        
        # if approaching limit, wait
        if len(self.rate_limit_window) > 1900:
            time.sleep(60)
        
        self.rate_limit_window.append(now)
    
    def get_project_info(self, project_id: str) -> Dict:
        """get basic project information"""
        project = self.gl.projects.get(project_id)
        
        return {
            'id': project.id,
            'name': project.name,
            'path_with_namespace': project.path_with_namespace,
            'web_url': project.web_url,
            'default_branch': project.default_branch
        }
