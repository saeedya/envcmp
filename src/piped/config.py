"""Configuration loader for piped."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class GitLabConfig:
    url: str
    token: str
    project_id: str

@dataclass
class GitHubConfig:
    token: str
    organization: str
    repository: str

@dataclass
class TerraformCloudConfig:
    token: str
    organization: str
    workspace: str

@dataclass
class Config:
    gitlab: GitLabConfig | None = None
    github: GitHubConfig | None = None
    terraform: TerraformCloudConfig | None = None

def load() -> Config:
    """Load configuration from environment variables."""
    load_dotenv()
    config = Config()

    if os.getenv("GITLAB_URL") and os.getenv("GITLAB_TOKEN") and os.getenv("GITLAB_PROJECT_ID"):
        config.gitlab = GitLabConfig(
            url=os.getenv("GITLAB_URL") or "",
            token=os.getenv("GITLAB_TOKEN") or "",
            project_id=os.getenv("GITLAB_PROJECT_ID") or "",
        )

    if os.getenv("GITHUB_TOKEN") and os.getenv("GITHUB_ORGANIZATION") and \
        os.getenv("GITHUB_REPOSITORY"):
        config.github = GitHubConfig(
            token=os.getenv("GITHUB_TOKEN") or "",
            organization=os.getenv("GITHUB_ORGANIZATION") or "",
            repository=os.getenv("GITHUB_REPOSITORY") or "",
        )

    if os.getenv("TERRAFORM_TOKEN") and os.getenv("TERRAFORM_ORGANIZATION") and \
        os.getenv("TERRAFORM_WORKSPACE"):
        config.terraform = TerraformCloudConfig(
            token=os.getenv("TERRAFORM_TOKEN") or "",
            organization=os.getenv("TERRAFORM_ORGANIZATION") or "",
            workspace=os.getenv("TERRAFORM_WORKSPACE") or "",
        )

    return config
