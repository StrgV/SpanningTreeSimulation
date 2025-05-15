def test_graph(graph):
    print("\n=== Graph Tests ===")
    
    # Test 1
    for switch in graph.switches:
        assert switch.switch_id > 0, f"Node {switch.name} has invalid ID: {switch.switch_id}"
    print("✓ All switch IDs > 0")
    
    # Test 2
    if graph.switches:
        min_id = min(switch.switch_id for switch in graph.switches)
        root_switches = [switch.name for switch in graph.switches if switch.switch_id == min_id]
        assert len(root_switches) == 1, f"Multiple potential root switches found: {root_switches}"
        print(f"✓ Unique root ID: {root_switches[0]} (ID: {min_id})")
    
    # Test 3
    if graph.switch_count > 0:
        visited = set()
        
        def dfs(switch_idx):
            visited.add(switch_idx)
            for neighbor_idx in range(graph.switch_count):
                if (neighbor_idx != switch_idx and 
                    graph.switches[switch_idx].links[neighbor_idx] > 0 and 
                    neighbor_idx not in visited):
                    dfs(neighbor_idx)
        
        dfs(0)
        assert len(visited) == graph.switch_count, "Graph is not connected"
        print("✓ Graph is connected")
    
    # Test 4
    for i, switch in enumerate(graph.switches):
        assert switch.links[i] == 0, f"Node {switch.name} has a self-loop"
    print("✓ No self-loops found")
    
    # Test 5
    edges_count = sum(1 for i in range(graph.switch_count) 
                      for j in range(i+1, graph.switch_count) 
                      if graph.switches[i].links[j] > 0)
    
    print(f"✓ Graph contains {graph.switch_count} switches and {edges_count} edges")
    print("==================\n")
    
    return {
        "switches_count": graph.switch_count,
        "edges_count": edges_count
    }
