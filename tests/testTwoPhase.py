import random

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

        n = int(input("Participant Size: "))
        abort = input("Abort? (y/n): ")
        # SUBCOMPONENTS
        self.Coordinator = TwoPhaseCommitCoordinator("Coordinator", componentinstancenumber)
        self.components.append(self.Coordinator)
        self.participants = list()

        for i in range(n):
            self.participants.append(TwoPhaseCommitParticipant(f"Participant {i}", componentinstancenumber))
            self.components.append((self.participants[i]))
            self.Coordinator.D(self.participants[i])
            self.participants[i].U(self.Coordinator)

        if abort.lower() == "y":
            i = random.randint(0, len(self.participants) - 1)
            self.participants[i].local_commit = TwoPhaseLocalCommitEventTypes.LOCAL_ABORT


def main():
    setAHCLogLevel(INFO)
    topo = Topology()
    topo.construct_single_node(Node, 0)

    start_time = datetime.datetime.now()
    topo.start()
    end_time = datetime.datetime.now()

    time.sleep(1)
    topo.exit()

    difference = end_time - start_time
    print(difference.total_seconds(), "s")


if __name__ == "__main__":
    main()
