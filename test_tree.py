import tree

def test_get_next_or():
    one = tree.Possibility ('3')
    two = tree.Possibility ('4 5')
    alt = tree.OrNode()
    alt.lNode = one
    alt.rNode = two
    assert(alt.get_next().value == '3')
    assert(alt.get_next().value == '4 5')


    one = tree.Possibility ('3')
    two = tree.Possibility ('4 5')
    alt2 = tree.OrNode()
    alt2.lNode = two
    alt2.rNode = one
    assert(alt2.get_next().value == '3')
    assert(alt2.get_next().value == '4 5')
    

def test_get_next_and():
    one = tree.Possibility ('3')
    two = tree.Possibility ('4 5')
    alt = tree.AndNode()
    alt.lNode = one
    alt.rNode = two
    assert(alt.get_next().value == '3 4 5')

def test_get_next_cycle():
    one = tree.Possibility ('1')
    alt = tree.CycleNode()
    alt.value = one
    assert(alt.get_next().value == '1')
    assert(alt.get_next().value == '1 1')
    assert(alt.get_next().value == '1 1 1')
    assert(alt.get_next().value == '1 1 1 1')

def test_get_next_cycle_or():
    one = tree.Possibility ('1')
    two = tree.Possibility ('2 3')
    cyc = tree.CycleNode()
    alt = tree.OrNode()
    alt.lNode = one
    alt.rNode = two
    cyc.value = alt
    assert(cyc.get_next().value == '1')
    assert(cyc.get_next().value == '2 3')
    assert(cyc.get_next().value == '1 1')
    assert(cyc.get_next().value == '1 1 1')
    assert(cyc.get_next().value == '1 2 3')
