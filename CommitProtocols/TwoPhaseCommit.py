"""
    Implementation of the Two Phase Commit Protocol.
"""

__author__ = "Yağızcan Pançak"
__contact__ = "yagizcan.pancak@metu.edu.tr"
__copyright__ = "Copyright 2024, WINSLAB"
__credits__ = ["Yağızcan Pançak"]
__date__ = "2024/04/15"
__deprecated__ = False
__email__ = "yagizcan.pancak@metu.edu.tr"
__license__ = "GPLv3"
__maintainer__ = "developer"
__status__ = "Production"
__version__ = "0.0.1"

from enum import Enum

from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import EventTypes, Event


class TwoPhaseCoordinatorEventTypes(Enum):
    VOTE_ABORT = "VOTE_ABORT"
    VOTE_COMMIT = "VOTE_COMMIT"
    COMMIT = "COMMIT"

class TwoPhaseParticipantEventTypes(Enum):
    VOTE_REQUEST = "VOTE_REQUEST"
    ABORT = "ABORT"
    COMMIT = "COMMIT"

class TwoPhaseCommitCoordinator(GenericModel):
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)

        self.number_of_participants = len(super().connectors)
        self.commit_count = 0
        self.eventhandlers[TwoPhaseCoordinatorEventTypes.COMMIT] = self.on_commit
        self.eventhandlers[TwoPhaseCoordinatorEventTypes.VOTE_COMMIT] = self.on_vote_commit
        self.eventhandlers[TwoPhaseCoordinatorEventTypes.VOTE_ABORT] = self.on_vote_abort

    def on_commit(self):
        self.number_of_participants = len(super().connectors)
        self.commit_count = 0
        self.send_down(Event(self, TwoPhaseParticipantEventTypes.VOTE_REQUEST))

    def on_vote_commit(self):
        self.commit_count += 1
        if self.commit_count == self.number_of_participants:
            self.send_down(Event(self, TwoPhaseParticipantEventTypes.COMMIT))

    def on_vote_abort(self):
        self.send_down(Event(self, TwoPhaseParticipantEventTypes.ABORT))
