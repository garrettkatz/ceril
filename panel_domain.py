"""
trigger, grasp, loosen, release, trigger

grasp(hand, thing): grasps the thing with hand
move(thing, position, rotation): moves the thing to given orientation
release(hand): releases whatever thing in hand
trigger(hand, toggle): changes toggle state with hand
loosen(hand, host bond, host thing, guest bond, guest thing): loosen thing bond with hand
unscrew(hand, screw):
    [grasp(hand, screw), loosen(hand, host bond, host thing, guest bond, guest thing)]
putdown(hand, thing, position, rotation)
    [[v move(thing, position, rotation)], release(hand)]
removescrew(hand, screw):
    [trigger, unscrew, putdown, trigger]
"""

def causes(v): 
    g = set() # set of possible causes
    states, tasks, args = zip(*v)
    if len(v) == 1:
        if tasks == ["release"]:
            hand = args[0][0]
            name = states[0].gripping[hand]
            thing = states[0].things[name]
            position = thing.position
            rotation = thing.rotation
            g.add((states[0], "putdown", (hand, name, position, rotation)))
