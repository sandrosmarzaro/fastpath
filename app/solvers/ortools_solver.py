from ortools.constraint_solver import pywrapcp, routing_enums_pb2


class ORToolsSolver:
    @classmethod
    def solve(
        cls,
        durantion_matrix: dict[str, list[int]],
        optmization_seconds: int = 10,
        vehicles_number: int = 1,
        pickup_index: int = 0,
    ) -> list[int]:
        manager = pywrapcp.RoutingIndexManager(
            len(durantion_matrix),
            vehicles_number,
            pickup_index,
        )
        routing = pywrapcp.RoutingModel(manager)

        def __cost_function(from_index: int, to_index: int) -> int:
            return int(
                durantion_matrix[manager.IndexToNode(from_index)][
                    manager.IndexToNode(to_index)
                ]
            )

        transit_callback_index = routing.RegisterTransitCallback(
            __cost_function
        )
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = optmization_seconds

        solution = routing.SolveWithParameters(search_parameters)

        if not solution:
            return list(range(len(durantion_matrix)))
        optimal_route = []
        index = routing.Start(0)
        while not routing.IsEnd(index):
            optimal_route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        return optimal_route
