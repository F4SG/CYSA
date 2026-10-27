from abc import ABC, abstractmethod
from collections.abc import Iterator
from .contracts import Conteo, Estado, PlanBorrador
class FuenteDeteccion(ABC):
    @abstractmethod
    def eventos(self) -> Iterator[Conteo]: ...
class Controlador(ABC):
    @abstractmethod
    def estado(self) -> Estado: ...
    @abstractmethod
    def enviar_plan(self, plan: PlanBorrador) -> None:
        """Reservado S2: implementación debe exigir validación, autorización y MFA."""
        raise NotImplementedError('Activación deshabilitada en S1')
