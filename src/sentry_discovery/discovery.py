#!/usr/bin/env python3
"""
Core discovery logic for Sentry resources
"""

import requests
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


@dataclass
class SentryResource:
    """Base class for Sentry resources"""

    id: str
    slug: str
    name: str
    raw_data: Dict[str, Any]


@dataclass
class SentryOrganization(SentryResource):
    """Sentry organization resource"""

    features: List[str]
    status: Dict[str, Any]


@dataclass
class SentryTeam(SentryResource):
    """Sentry team resource"""

    organization: str
    members: List[Dict[str, Any]]
    projects: List[str]


@dataclass
class SentryProject(SentryResource):
    """Sentry project resource"""

    organization: str
    platform: str
    teams: List[Dict[str, Any]]
    status: str
    features: List[str]
    options: Dict[str, Any]


class SentryAPIError(Exception):
    """Sentry API error"""

    def __init__(self, message: str, status_code: int = None, response: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class SentryDiscovery:
    """Main discovery class for Sentry resources"""

    def __init__(
        self,
        auth_token: str,
        base_url: str = "https://sentry.io/api/0",
        timeout: int = 30,
        retry_attempts: int = 3,
        verbose: bool = False,
    ):
        self.auth_token = auth_token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.verbose = verbose

        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "User-Agent": "sentry-terraform-discovery/1.0.0",
        }

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests

        logger.info(f"Initialized SentryDiscovery with base_url: {self.base_url}")

    def _make_request(
        self, endpoint: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Sentry API with retry logic"""
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))

        for attempt in range(self.retry_attempts + 1):
            try:
                # Rate limiting
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                if time_since_last < self.min_request_interval:
                    time.sleep(self.min_request_interval - time_since_last)

                logger.debug(f"Making request to {url} (attempt {attempt + 1})")

                response = self.session.get(url, params=params, timeout=self.timeout)

                self.last_request_time = time.time()

                # Handle different response codes
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 204:
                    return {}
                elif response.status_code == 404:
                    logger.warning(f"Resource not found: {url}")
                    return {}
                elif response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limited, waiting {retry_after} seconds")
                    time.sleep(retry_after)
                    continue
                elif response.status_code in [401, 403]:
                    raise SentryAPIError(
                        f"Authentication failed: {response.status_code} - {response.text}",
                        response.status_code,
                        response.text,
                    )
                else:
                    response.raise_for_status()

            except requests.exceptions.Timeout:
                if attempt < self.retry_attempts:
                    wait_time = 2**attempt  # Exponential backoff
                    logger.warning(f"Request timeout, retrying in {wait_time} seconds")
                    time.sleep(wait_time)
                    continue
                raise SentryAPIError(
                    f"Request timeout after {self.retry_attempts} retries"
                )

            except requests.exceptions.ConnectionError:
                if attempt < self.retry_attempts:
                    wait_time = 2**attempt
                    logger.warning(f"Connection error, retrying in {wait_time} seconds")
                    time.sleep(wait_time)
                    continue
                raise SentryAPIError(
                    f"Connection error after {self.retry_attempts} retries"
                )

            except requests.exceptions.RequestException as e:
                raise SentryAPIError(f"Request failed: {str(e)}")

        raise SentryAPIError(
            f"Failed to make request after {self.retry_attempts + 1} attempts"
        )

    def get_organizations(self) -> List[SentryOrganization]:
        """Get all organizations the token has access to"""
        logger.info("Fetching organizations")

        data = self._make_request("/organizations/")
        if not isinstance(data, list):
            logger.error(f"Expected list, got {type(data)}")
            return []

        organizations = []
        for org_data in data:
            org = SentryOrganization(
                id=org_data["id"],
                slug=org_data["slug"],
                name=org_data["name"],
                features=org_data.get("features", []),
                status=org_data.get("status", {}),
                raw_data=org_data,
            )
            organizations.append(org)

        logger.info(f"Found {len(organizations)} organizations")
        return organizations

    def get_teams(self, org_slug: str) -> List[SentryTeam]:
        """Get all teams in the organization"""
        logger.info(f"Fetching teams for organization: {org_slug}")

        data = self._make_request(f"/organizations/{org_slug}/teams/")
        if not isinstance(data, list):
            return []

        teams = []
        for team_data in data:
            # Get team members
            members = self.get_team_members(org_slug, team_data["slug"])

            team = SentryTeam(
                id=team_data["id"],
                slug=team_data["slug"],
                name=team_data["name"],
                organization=org_slug,
                members=members,
                projects=team_data.get("projects", []),
                raw_data=team_data,
            )
            teams.append(team)

        logger.info(f"Found {len(teams)} teams")
        return teams

    def get_team_members(self, org_slug: str, team_slug: str) -> List[Dict[str, Any]]:
        """Get all members of a specific team"""
        logger.debug(f"Fetching members for team: {org_slug}/{team_slug}")

        data = self._make_request(
            f"/organizations/{org_slug}/teams/{team_slug}/members/"
        )
        if not isinstance(data, list):
            return []

        return data

    def get_projects(self, org_slug: str) -> List[SentryProject]:
        """Get all projects in the organization"""
        logger.info(f"Fetching projects for organization: {org_slug}")

        data = self._make_request(f"/organizations/{org_slug}/projects/")
        if not isinstance(data, list):
            return []

        projects = []
        for project_data in data:
            # Get project teams
            teams = self.get_project_teams(org_slug, project_data["slug"])

            # Get project details if needed
            details = self.get_project_details(org_slug, project_data["slug"])

            project = SentryProject(
                id=project_data["id"],
                slug=project_data["slug"],
                name=project_data["name"],
                organization=org_slug,
                platform=project_data.get("platform", "other"),
                teams=teams,
                status=project_data.get("status", "unknown"),
                features=project_data.get("features", []),
                options=details.get("options", {}),
                raw_data={**project_data, **details},
            )
            projects.append(project)

        logger.info(f"Found {len(projects)} projects")
        return projects

    def get_project_teams(
        self, org_slug: str, project_slug: str
    ) -> List[Dict[str, Any]]:
        """Get teams assigned to a specific project"""
        logger.debug(f"Fetching teams for project: {org_slug}/{project_slug}")

        data = self._make_request(
            f"/organizations/{org_slug}/projects/{project_slug}/teams/"
        )
        if not isinstance(data, list):
            return []

        return data

    def get_project_details(self, org_slug: str, project_slug: str) -> Dict[str, Any]:
        """Get detailed information about a specific project"""
        logger.debug(f"Fetching details for project: {org_slug}/{project_slug}")

        return self._make_request(f"/organizations/{org_slug}/projects/{project_slug}/")

    def discover_all(
        self,
        target_org_slug: Optional[str] = None,
        projects_only: bool = False,
        teams_only: bool = False,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> Dict[str, Any]:
        """Discover all resources in Sentry"""
        logger.info("Starting comprehensive discovery")

        if progress_callback:
            progress_callback(10)

        # Get organizations
        orgs = self.get_organizations()
        if not orgs:
            logger.error("No organizations found or invalid token")
            return {}

        # Use specified org or first available
        if target_org_slug:
            org = next((o for o in orgs if o.slug == target_org_slug), None)
            if not org:
                raise ValueError(f"Organization '{target_org_slug}' not found")
        else:
            org = orgs[0]
            logger.info(f"Using organization: {org.name} ({org.slug})")

        if progress_callback:
            progress_callback(20)

        result = {"organization": org.raw_data, "teams": [], "projects": []}

        # Get teams if not projects-only
        if not projects_only:
            logger.info("Discovering teams...")
            teams = self.get_teams(org.slug)
            result["teams"] = [self._serialize_team(team) for team in teams]

            if progress_callback:
                progress_callback(60)

        # Get projects if not teams-only
        if not teams_only:
            logger.info("Discovering projects...")
            projects = self.get_projects(org.slug)
            result["projects"] = [
                self._serialize_project(project) for project in projects
            ]

            if progress_callback:
                progress_callback(90)

        if progress_callback:
            progress_callback(100)

        logger.info("Discovery completed successfully")
        return result

    def _serialize_team(self, team: SentryTeam) -> Dict[str, Any]:
        """Serialize team object to dictionary"""
        return {
            "id": team.id,
            "slug": team.slug,
            "name": team.name,
            "organization": team.organization,
            "members": team.members,
            "projects": team.projects,
            **team.raw_data,
        }

    def _serialize_project(self, project: SentryProject) -> Dict[str, Any]:
        """Serialize project object to dictionary"""
        return {
            "id": project.id,
            "slug": project.slug,
            "name": project.name,
            "organization": project.organization,
            "platform": project.platform,
            "teams": project.teams,
            "status": project.status,
            "features": project.features,
            "options": project.options,
            **project.raw_data,
        }

    def test_connection(self) -> bool:
        """Test the API connection and authentication"""
        try:
            logger.info("Testing Sentry API connection")
            orgs = self.get_organizations()
            return len(orgs) > 0
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def __del__(self):
        """Clean up session"""
        if hasattr(self, "session"):
            self.session.close()
