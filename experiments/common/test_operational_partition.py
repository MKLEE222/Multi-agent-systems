from operational_partition import (
    behavior_signatures_exact,
    partitions_from_behavior_signatures,
    nested_partition_check,
    refinement_relation,
    information_burden_bits,
)

states=["a","b","c","d"]
obs={"a":0,"b":0,"c":1,"d":1}
actions=["x"]

def succ(s,a):
    table={"a":"a","b":"c","c":"c","d":"d"}
    return ("OK",table[s])

sigs=behavior_signatures_exact(states,obs,actions,succ,2)
parts=partitions_from_behavior_signatures(sigs)
assert len(parts[0])==2,parts
assert len(parts[1])==3,parts
assert len(parts[2])==3,parts
chk=nested_partition_check(parts[0],parts[1])
assert chk["is_refinement"],chk
assert chk["delta_information_bits"]>0
stats=refinement_relation(parts[0],parts[1])
assert stats["under_refinement_count"]>0
assert information_burden_bits(parts[1])>information_burden_bits(parts[0])
print("OACR M1 exact-partition self-test PASS")
