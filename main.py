#!/usr/bin/env python
import csv
import math

class Schedule:
    def __init__(self, path: str):
        '''Initialization of state'''
        # All schedules from .csv file
        self.schedules = self._get_schedules(path)
        # All stations that are in the schedules
        self.stations = self._get_stations()
        # The weight matrix of the smallest schedules
        self._weight_matrix: list[list] = None
        # Returns a weight of a schedule
        self._get_weight: function = None
        # Checks the result schedule and schedules
        self._is_exact_schedule: function = None
        # Formats the result
        self._formatting_result: function = None
        # Search type
        self._search_mode: str = None
    
    def _get_schedules(self, path: str) -> list[list]:
        '''Returns schedules from .csv file'''
        with open(path, newline='') as csvfile:
            sch_reader = csv.reader(csvfile, delimiter=';', quotechar='\n')
            return  [row for row in sch_reader]
    
    def _get_stations(self) -> list[str]:
        '''Returns all stations from schedules'''
        return sorted({schedule[1] for schedule in self.schedules} |
                            {schedule[2] for schedule in self.schedules})
    
    def _get_weight_matrix(self):
        '''Return the weight matrix of the smallest schedules'''
        num_sts = len(self.stations)
        weight_matrix = [[math.inf] * num_sts for i in range(num_sts)]
        for schedule in self.schedules:
            i, j = (self.stations.index(schedule[1]),
                     self.stations.index(schedule[2]))
            weight = self._get_weight(schedule)
            if weight < weight_matrix[i][j]:
                weight_matrix[i][j] = weight
        return weight_matrix
    
    def _date_to_num(self, date: str) -> int:
        '''Converts a date to a number'''
        date = date.split(":")
        return int(date[0]) * 60 + int(date[1])

    def _num_to_date(self, num: int) -> str:
        '''Converts a number to a date'''
        return "{:02}:{:02}:00".format(num // 60, num % 60)

    def _get_weight_from_time(self, departure: str, arrival: str) -> int:
        '''Returns the dates weight'''
        num1, num2 = self._date_to_num(departure), self._date_to_num(arrival)
        return num2 - num1 if num1 < num2 else (num2 + 1440) - num1

    def _nearest_neighbor_algorithm(self, graph: list[list], start_vortex=None):
        '''
        The Nearest Neighbor Algorithm for solving The Traveling Salesman Problem
        _________________________________________________________________________
        Initialize all vertices as unvisited.
        Select an arbitrary vertex, set it as the current vertex u. Mark u as visited.
        Find out the shortest edge connecting the current vertex u and an unvisited vertex v.
        Set v as the current vertex u. Mark v as visited.
        If all the vertices in the domain are visited, then terminate.
        _________________________________________________________________________
        Return the best route and "minimum" weights in a tuple like ([0, 4, 1, 3, 2], 312)
        '''
        current_vortex = start_vortex if start_vortex != None else 0
        vortices = len(graph)
        passed_vortices = [current_vortex]
        route_weight = 0

        key_for_min = lambda x: x[1]

        while True:
            current_row = [(i, weight) for i, weight in enumerate(graph[current_vortex])
                            if self._check_vortex(graph, passed_vortices, i)]
            current_vortex, min_weight = min(current_row, key=key_for_min)
            passed_vortices.append(current_vortex)
            route_weight += min_weight if min_weight != math.inf else 0
            if len(passed_vortices) == vortices: break
        
        return passed_vortices, route_weight

    def _check_vortex(self, graph: list[list], passed_vortices: list, vortex: int):
        '''Checks whether neighboring vertices will be blocked when this vertex is selected.'''
        if vortex in passed_vortices: return False
        conn_vors = [i for i, vor in enumerate(graph[vortex])
                        if vor != math.inf and vor not in passed_vortices]
        checked = [vor for vor in conn_vors
                    if self._isclosevortex(graph, passed_vortices, vor)]
        return True if not checked else False

    def _isclosevortex(self, graph: list[list], passed_vortices: list, vortex: int):
        '''Checks if the vertex is blocked'''
        free_vort = len([vor for i, vor in enumerate(graph[vortex])
                        if vor != math.inf and i not in passed_vortices])
        return False if free_vort > 1 or len(passed_vortices) >= len(graph) - 2 else True
    
    def set_search_by(self, param: str) -> None:
        '''Sets the parameter to search'''
        match param:
            case "price":
                self._get_weight = (lambda schedule: float(schedule[3]))
                self._is_exect_schedule = (lambda sch, rout:
                                sch[1:3] + [str(float(sch[3]))] == rout[0])
                self._formatting_result = (lambda x: f"{round(x, 2)}$")
                self._search_mode = param
            case "time":
                self._get_weight = (lambda schedule:
                        self._get_weight_from_time(schedule[4], schedule[5]))
                self._is_exect_schedule = (lambda schedule, route: schedule[1:3]
                 + [str(self._get_weight_from_time(*schedule[4:]))] == route[0])
                self._formatting_result = (lambda x: 
                                f"{x // 60} hours and {x % 64} minutes")
                self._search_mode = param
            case default:
                raise Exception(f"{param} is incorrect search mode.")

    def find_the_best_route(self) -> None:
        '''Finds the best route and prints it'''
        self._weight_matrix = self._get_weight_matrix()
        num_sts = len(self.stations)
        nna_result = self._nearest_neighbor_algorithm(self._weight_matrix, 1)
        route = []
        # Finds a route based on the NNA result
        for i, p in enumerate(nna_result[0]):
            route.append([self.stations[p], self.stations[nna_result[0][(i + 1) % num_sts]],
                str(self._weight_matrix[p][nna_result[0][(i + 1) % num_sts]])])

        del route[-1]
        formatted = self._formatting_result(nna_result[1])
        text = f'The "best" route by {self._search_mode} '
        text += f'for {formatted} through each station:'
        print(text)
        while route:
            for schedule in self.schedules:
                if self._is_exect_schedule(schedule, route):
                    print(schedule)
                    del route[0]
                    break

if __name__ == '__main__':
    instance = Schedule(r'test_task_data.csv')
    instance.set_search_by("price")
    instance.find_the_best_route()
    instance.set_search_by("time")
    instance.find_the_best_route()
