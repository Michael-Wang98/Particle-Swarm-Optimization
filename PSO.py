from random import random, randrange
from math import sqrt, floor
import matplotlib.pyplot as pyot

# Global variables
COUNTER_MAX = 50  # maximum number of iterations without improvement before the program terminates
VERSION = "inertial"  # determines velocity version used, choice of simple, inertial, constrict and guaranteed
SYNC = False  # synchronous or asynchronous update, currently not in use as program only has async mode
SIZE = 50  # number of particles
V_MAX = 5  # maximum particle velocity

W = 0.792  # should be less than 1
ci1 = 1.4944  # inertial c value, should be greater than 1
ci2 = ci1  # keep them the same for now

cc1 = 2.05  # constriction c value
cc2 = cc1  # keep them the same for now
phi = cc1 + cc2  # phi value for the constriction method
K = 2/abs(2-phi-sqrt(phi**2 - 4 * phi))

tau = None  # position of current best
cg1 = 1.4944  # guaranteed convergence c value
cg2 = cg1  # keep them the same for now
es = 15  # epsilon of success
ef = 5  # epsilon of failure
N_best = 1000000  # global best, initialize to an unusably large number


class Particle:
    def __init__(self):
        self.x_velocity = 0
        self.y_velocity = 0
        self.x_position = randrange(-5, 5)
        self.y_position = randrange(-5, 5)
        self.p_best = (self.x_position, self.y_position)
        self.optimum = hump_camel(self.x_position, self.y_position)

    def position(self):
        self.x_position += self.x_velocity
        self.y_position += self.y_velocity

    def velocity(self, version):
        if version == "simple":
            self.x_velocity = max(min(self.x_velocity + ci1 * random() * (self.p_best[0] - self.x_position) + ci2 * random() * (N_best - self.x_position), V_MAX), -V_MAX)
            self.y_velocity = max(min(self.y_velocity + ci1 * random() * (self.p_best[1] - self.y_position) + ci2 * random() * (N_best - self.y_position), V_MAX), -V_MAX)
        elif version == "inertial":
            self.x_velocity = max(min(W * self.x_velocity + ci1 * random() * (self.p_best[0] - self.x_position) + ci2 * random() * (N_best - self.x_position), V_MAX), -V_MAX)
            self.y_velocity = max(min(W * self.y_velocity + ci1 * random() * (self.p_best[1] - self.y_position) + ci2 * random() * (N_best - self.y_position), V_MAX), -V_MAX)
        elif version == "constrict":
            self.x_velocity = max(min(K * floor(self.x_velocity + cc1 * random() * (self.p_best[0] - self.x_position) + cc2 * random() * (N_best - self.x_position)), V_MAX), -V_MAX)
            self.y_velocity = max(min(K * floor(self.y_velocity + cc1 * random() * (self.p_best[1] - self.y_position) + cc2 * random() * (N_best - self.y_position)), V_MAX), -V_MAX)
        else:
            print("ERROR: TYPO")

    def guaranteed_velocity(self, rho):
        self.x_velocity = max(min(W * self.x_velocity - tau.x_position + N_best + rho * (1 - 2 * random()), V_MAX), -V_MAX)
        self.y_velocity = max(min(W * self.x_velocity - tau.y_position + N_best + rho * (1 - 2 * random()), V_MAX), -V_MAX)

    def update(self):
        fitness = hump_camel(self.x_position, self.y_position)
        if fitness < self.optimum:
            self.p_best = (self.x_position, self.y_position)
            self.optimum = fitness
        return fitness


def hump_camel(x, y):
    return (4 - 2.1*x**2 + (x**4)/3)*x**2 + x*y + (-4 + 4*y**2)*y**2


if __name__ == '__main__':
    stale = 0  # use a counter to determine when the solutions are no longer improving at a useful rate
    iterations = 0  # count total iterations for graphing sake
    best_iteration = []  # best fitness per iteration
    average_iteration = []  # average fitness per iteration

    # initialize the swarm
    swarm = []
    for part in range(SIZE):
        swarm.append(Particle())

    if VERSION == "guaranteed":
        rho = 1
        success_counter = 0
        fail_counter = 0
        # determine the best placed particle initially
        for O in swarm:
            pos = O.update()
            if pos < N_best:
                N_best = pos
                tau = O

        while stale < COUNTER_MAX:  # main loop for guaranteed
            total = 0
            flag = False
            for P in swarm:
                if P == tau:
                    P.guaranteed_velocity(rho)
                else:
                    P.velocity("inertial")
                P.position()
                best = P.update()
                total += best
                if best < N_best:
                    N_best = best
                    tau = P
                    stale = 0  # found a better solution reset the staleness counter
                    flag = True  # success

            if flag:  # success
                fail_counter = 0
                success_counter += 1
                if success_counter > es:
                    rho = rho/2
            else:  # failure
                success_counter = 0
                fail_counter += 1
                if fail_counter > ef:
                    rho = rho/2

            stale += 1
            iterations += 1
            print(str(N_best) + ", " + str(total / SIZE))
            best_iteration.append(N_best)
            average_iteration.append(total / SIZE)

    elif VERSION == "simple" or VERSION == "inertial" or VERSION == "constrict":
        while stale < COUNTER_MAX:  # main loop for every version except guaranteed
            total = 0
            for P in swarm:
                P.velocity(VERSION)
                P.position()
                best = P.update()
                total += best
                if best < N_best:
                    N_best = best
                    stale = 0  # found a better solution reset the staleness counter

            stale += 1
            iterations += 1
            print(str(N_best) + ", " + str(total/SIZE))
            best_iteration.append(N_best)
            average_iteration.append(total/SIZE)

    else:
        print("Error: TYPO")

    # pyot.plot(range(0, iterations), best_iteration)
    # pyot.ylabel("Minimum")
    pyot.plot(range(0, iterations), average_iteration)
    pyot.ylabel("Average")
    pyot.xlabel("Iteration")
    pyot.show()
