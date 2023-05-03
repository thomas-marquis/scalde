from abc import ABC, abstractmethod

from .models import AccessTokenDict, IdTokenDict, PublicKey, TokenDict


class AuthStore(ABC):
    @property
    def access_token(self) -> AccessTokenDict | None:
        pass

    @access_token.setter
    @abstractmethod
    def access_token(self, value: AccessTokenDict) -> None:
        pass

    @property
    def id_token(self) -> IdTokenDict | None:
        pass

    @id_token.setter
    @abstractmethod
    def id_token(self, value: IdTokenDict) -> None:
        pass

    @property
    def refresh_token(self) -> TokenDict | None:
        pass

    @refresh_token.setter
    @abstractmethod
    def refresh_token(self, value: TokenDict) -> None:
        pass

    @property
    def public_keys(self) -> list[PublicKey] | None:
        pass

    @public_keys.setter
    @abstractmethod
    def public_keys(self, value: list[PublicKey]) -> None:
        pass

    @abstractmethod
    def __contains__(self, key: str) -> bool:
        pass

    @abstractmethod
    def __delattr__(self, __name: str) -> None:
        pass
