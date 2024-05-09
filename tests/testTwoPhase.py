from adhoccomputing.Generics import *
from adhoccomputing.Experimentation.Topology import Topology
from CommitProtocols.TwoPhaseCommit import *
import time

class Node(GenericModel):
    def on_init(self, eventobj: Event):
        self.Coordinator.on_commit()


    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None,
                 num_worker_threads=1, topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads,
                         topology)
        # SUBCOMPONENTS
        self.Coordinator = TwoPhaseCommitCoordinator("Coordinator", componentinstancenumber)
        self.P1 = TwoPhaseCommitParticipant("Participant 1", componentinstancenumber, local_commit=TwoPhaseLocalCommitEventTypes.ABORT)
        self.P2 = TwoPhaseCommitParticipant("Participant 2", componentinstancenumber)
        self.P3 = TwoPhaseCommitParticipant("Participant 3", componentinstancenumber)

        self.components.append(self.Coordinator)
        self.components.append(self.P1)
        self.components.append(self.P2)
        self.components.append(self.P3)

        ## CONNECTION using U (up) D (down) P (peer) functions
        self.Coordinator.D(self.P1)
        self.Coordinator.D(self.P2)
        self.Coordinator.D(self.P3)

        self.P1.U(self.Coordinator)
        self.P2.U(self.Coordinator)
        self.P3.U(self.Coordinator)


def main():
  #setAHCLogLevel(DEBUG)
  topo = Topology();
  topo.construct_single_node(Node, 0)
  topo.start()
  time.sleep(1)
  topo.exit()

if __name__ == "__main__":
  main()