from abc import ABC, abstractmethod
from typing import Optional

from terratalk.terraform_out import TerraformOut


class CommentDriver(ABC):
    def __init__(self) -> None:
        self.type: Optional[str] = None
        self.server: Optional[str] = None
        self.project_key: Optional[str] = None
        self.pull_request_id: Optional[int] = None
        self.repository_slug: Optional[str] = None

    @abstractmethod
    def add(self, workspace: str, tf_out: TerraformOut):
        pass

    @abstractmethod
    def detect(self) -> bool:
        """Returns True if the environment matches this driver."""
        pass
