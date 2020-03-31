# ceril

`ceril` is a framework for knowledge-based robotic imitation learning.  It leverages human-engineered causal knowledge to infer the intentions behind a human demonstrator's actions.  Then it decomposes those intentions into a plan of action more suitable for a robot.  The theoretical underpinnings of this framework are detailed in [this paper](https://doi.org/10.1109/TCDS.2017.2651643).

## Quick start

To quickly get started using `ceril`, follow the steps below.  These use a simplified robotics scenario as an example and show how to apply `ceril` in that situation.

0. Clone this repository to a local `ceril/` directory on your computer.

0. Separately install the [SciPy stack](https://www.scipy.org/) (at least `numpy`, `scipy`, and `matplotlib`).  These are used for various numerical processing requirements of `ceril`.

0. Separately install [PyTorch](https://pytorch.org/).  It is used here for computing gradients during robotic motion planning.

0.  All scripts in this walk-through should be run on the command line from within the `ceril/src` working directory, but you could configure your system or package `ceril` if you would like them to be available in other directories.

1. Separately install [SMILE](https://github.com/dwhuang/SMILE/releases/tag/v1.1.0).  This is a virtual demonstration environment with simulated physics in which you can drag and drop objects on a tabletop and record your actions.  It saves the recording in text format.  `ceril/src/parse_demo.py` is an included module that can parse SMILE's demo format.  If you do not want to install SMILE right now, you can skip ahead and use the pre-recorded SMILE files in `ceril/demos/test`.  If you record demonstrations a different way, you can still use `ceril`, but will need to parse them into `ceril`'s required format yourself.

2. Design your demonstration environment by defining the relevant objects and interactions using SMILE's extensible XML schema.  The SMILE documentation contains many details on the XML schema.  For the purpose of this walk-through, you can use the pre-defined files included in `ceril/tablesetup/`.  These files define a faux electrical panel in which a switch needs to be toggled and a screw needs to be removed, shown below.  To use the pre-defined files with SMILE, you can copy them to the _smiledir_`/tablesetup` folder, where _smiledir_ is the directory where you installed SMILE.  Alternatively, if you plan to edit them and commit your changes in the `ceril` repository, you can setup soft-links in _smiledir_`/tablesetup` that point to the repository.  On Linux you can do this with a command like:

`ln -s /path/to/ceril/tablesetup/* ./`

executed in _smiledir_`/tablesetup`.  But be careful that files with the same names don't already exist in _smiledir_`/tablesetup`.  And omit the trailing `/` when removing soft-links to directories.  Similarly for the `ceril/tablesetup/stl` sub-directory.

![Smile Panel](https://user-images.githubusercontent.com/6537102/77976367-d0302d80-72ca-11ea-8df4-0db7aeec6592.png)

3. Run SMILE and record a demonstration as explained in the SMILE documentation.  With Intel graphics drivers, you may need to disable antialiasing in the SMILE launch dialog to avoid a null pointer crash.  When you finish the demonstration, it will be written to text format in _smiledir_`/demo`.  You can copy or move this demo directory somewhere else for safe-keeping so it does not get overwritten the next time you use SMILE.  This is how we generated the files in `ceril/demos/test`.  Normally, `ceril/src/parse_demo.py` is loaded as a module, but the code under the `main` block provides some example usage.  If you run `parse_demo.py` as a script, the `main` block will parse the test demo and draw a simple rendering of the first and last state, (shown below) with bounding boxes of the objects on the tabletop.  The `parse_demo` routine produces a list of actions that were performed during the demo along with the state of the tabletop environment before and after each action.  These states are represented by the `SmileState` class in `ceril/src/smile_state.py`.

![demo_render](https://user-images.githubusercontent.com/6537102/77977695-631e9700-72ce-11ea-9be5-5681d2172d36.png)

4. Next you need to engineer some pieces of causal knowledge for `ceril` to use as building blocks when it infers a demonstrations intentions or forms its own robotic plan.  `ceril` uses [copct](https://github.com/garrettkatz/copct) to infer intentions, and [pyhop](https://bitbucket.org/dananau/pyhop/src/default/) to form its own plans.  These two libraries are essentially inverses of one another, but both are based on an automated planning formalism called [Hierarchical Task Networks (HTNs)](https://en.wikipedia.org/wiki/Hierarchical_task_network).  You do not need to install either of these repositories, since the necessary files are copied (unchanged) and included in `ceril/src` already.

Both `copct` and `pyhop` involve the notion of a "domain", which is a definition of the behaviors available to the robotic agent, and the effects those behaviors have on the environment.  The behaviors are _hierarchical_ in that some abstract behaviors (e.g., discarding a screw) cause an agent to perform more concrete behaviors (e.g, closing a gripper).  Behaviors are also called "tasks" in `pyhop` and "intentions" in `copct`.  Following `pyhop` terminology, the most concrete tasks are called "HTN operators", and all more abstract tasks are called "HTN methods".

An example domain definition for the electrical panel task is given in `ceril/src/panel_domain.py`.  It contains the following components, which are needed in any `ceril` domain definition:

- `htn_operators()`: A function whose return value is a dictionary that maps HTN operator names (strings) to function handles.  Each operator function can take any number of arguments, but the first argument represents the current state before the agent performs the operation.  It should always be an instance of the `State` class in `ceril/src/planning.py`.  If the behavior is not admissible in the current state, then the operator function should return `False`.  Otherwise, it should return the new state that results after the operation is complete.

- `htn_methods()`: A function whose return value is a dictionary that maps HTN method names (strings) to function handles.  As with operators, the first argument to a method must be a `State` instance.  If the method is not admissible in the current state, then the method function should return `False`.  Otherwise, it should return a sequence of more concrete tasks to perform.  Each element of this sequence is a 2-tuple.  The first element of the tuple is the name of an method or operator, and the second element is itself a tuple of input arguments (excluding the current state).

- `causes(v)`: A function that conceptually is the inverse of the HTN methods.  Following `copct` notation, the input `v` is a sequence of tasks.  Each element of this sequence is a 3-tuple.  The first element of the 3-tuple is the state immediately before the task is performed.  The second is the name of the task (a string).  The third element is itself a tuple of input arguments (excluding the current state).  The output of `causes` is a set of all parent tasks that could have produced the sequence `v`.  Each parent task in this set has the same 3-tuple format as the elements of `v`.  Since `copct` relies on the `Set` data structure for this, each 3-tuple must be hashable, including the first element (representing the current state)  The `SmileState.tuplify()` and `from_tuple` functions in `smile_state.py` serve to convert `SmileState` instances to and from (hashable) tuples in `causes`.

- `M_causes`: An `int` variable.  It is intended as a constant whose value is the length of the longest possible `v` that could be directly caused by any parent task in the domain.  `copct` relies on this upper bound to optimize its running time.

5. If you plan to use `ceril` with physical robots, you will most likely need to interface the HTN operators with separate libraries for low-level routines such as object localization and tracking, collision detection, motion and grasp planning, and so on.  In the panel example, we illustrate this with a simplistic interface to a robot (called "tiger") with a mobile base and a UR10 arm.  For simplicity we only focus on a basic motion planner and ignore computer vision, obstacle avoidance, etc.  We designed this example interface as follows:

- The `State` class in `planning.py` has two fields: `smile`, which is an instance of `SmileState`, and `robot`, which is an instance of the class `TigerState` in `tiger_state.py`.  The latter is used to track and plan the state of the robot (base position and joint angles).

- A `Kinematics` class in `kinematic_chain.py` is used to calculate forward kinematics of the UR10 arm.  The forward kinematics use the [Denavit-Hartenberg parameterization](https://en.wikipedia.org/wiki/Denavit%E2%80%93Hartenberg_parameters).  All vectors and matrices involved are wrapped in `torch.Tensor` objects so that the forward kinematics can be automatically differentiated during motion planning.

- The `TigerState` class includes a function `plan_motion(world, target)`.  Although we do not consider obstacle avoidance in this example, we included the `world` argument as a placeholder since it would be needed in that case.  `target` is a 4x4 `numpy` array representing the target rotation and position of the UR10 end effector in homogenous coordinates.  We implemented `plan_motion` using off-the-shelf local minimization routines in `scipy`.  To supply the needed gradients, we wrapped the Tiger base coordinates and arm joints in gradient-enabled `torch.Tensor` objects before computing the forward kinematics, then differentiated the squared Frobenius norm between the target and current end-effector matrices.  Although `tiger_state` will usually be imported as a module, you can run it as a script to see a sample motion planning result, shown below.  The black wireframe represents tiger before planning, and the green represents tiger after planning to reach the red target position.

![tiger_ik](https://user-images.githubusercontent.com/6537102/77981452-fdcfa380-72d7-11ea-8831-334f95419c94.png)

- To implement different and/or more realistic robot models, `TigerState` should be replaced with another more sophisticated class that is used as the `robot` field of the `State` class in `planner.py`.

7. With all the pieces in place, you are ready to use `ceril`.  The full imitation pipeline is implemented by the method `imitate` in `ceril/src/ceril.py`. 

- The inputs to `imitate` are as follows: The first input is the domain module (e.g., `domain` is supplied as an argument after `import panel_domain`).  The second argument is the demonstration sequence, in the same format as `v` in the domain `causes` function.  The third argument is an instance of the `State` class in `planner.py`, and represents the environment the robot is in when it needs to begin imitating (potentially different from the initial state during the demonstration).  The fourth is an optional verbosity argument (higher integer values lead to more console debugging output).

- The output of `imitate` is a three tuple.  The first element is a boolean indicator of success.  The second element is a list of `State` instances representing the state before and after each action in the resulting plan.  The third is a list of actions.  Each action is a tuple whose first element is its HTN operator name, and whose remaining elements are its additional arguments (excluding current state).

Running `ceril.py` as a script will run its `main` block, which loads the `test` demo included in this repository, infers the demonstrators intentions, and then forms a robotic plan.  It will then display wireframe renderings for the intermediate states during plan execution, one at a time.  Hit `Enter` on the command line where you ran the script to advance to the next state.  One intermediate state is shown below, in which Tiger has grasped the screw that needs to be replaced.  The motion planner found a "solution" where the gripper reaches the target but the base intersects the tabletop.  If `TigerState` were extended or replaced with a more sophisticated obstacle-aware motion planner, this could be improved.

![interstate](https://user-images.githubusercontent.com/6537102/77982752-12616b00-72db-11ea-9992-246436b7c64e.png)
