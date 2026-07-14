"""Codex Hereticus — error machinery. See docs 06-heresies.md."""
from __future__ import annotations


class Profanatio(Exception):
    """Compile/load-time rejection. Exit code II."""

    def __init__(self, code: str, genus: str, message: str,
                 archivum: str = "?", versus: int = 0):
        super().__init__(message)
        self.code = code          # e.g. "P-XIV"
        self.genus = genus
        self.nuntius = message
        self.archivum = archivum
        self.versus = versus


class Heresis(Exception):
    """Runtime heresy. Minor = catchable, Major = not."""

    def __init__(self, genus: str, nuntius: str, *, versus: int = 0,
                 archivum: str = "?", gradus: int = 0, major: bool = False,
                 origo: "Heresis | None" = None):
        super().__init__(nuntius)
        self.genus = genus
        self.nuntius = nuntius
        self.versus = versus
        self.archivum = archivum
        self.gradus = gradus
        self.major = major
        self.origo = origo
        self.vestigium: list[str] = []


class IraMachinae(Exception):
    """Terraform subprocess failure. Exit code III."""

    def __init__(self, message: str, stderr: str = ""):
        super().__init__(message)
        self.nuntius = message
        self.stderr = stderr


MINOR = dict(major=False)
MAJOR = dict(major=True)

# canonical hint table (subset)
HINTS = {
    "divisio_nihili": "guard the divisor — SI divisor == N TUNC ...",
    "clavis_ignota": "use habet(tabula, clavis) or accipe(tabula, clavis, defectus)",
    "typus_profanus": "transmute explicitly: numerus(...), scriptum(...), fractio(...)",
    "vas_ignotum": "declare the vessel first: DECLARO nomen : TYPUS = ...",
    "sanctum_violatum": "that binding is consecrated; declare it with DECLARO if it must change",
    "reditus_deest": "every path of a non-NIHIL rite must REDDO",
    "relatio_differata_tacta": "deferred references may only appear in resource attributes and PROFITEOR",
}
