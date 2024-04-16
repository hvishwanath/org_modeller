import yaml
import logging
from collections import defaultdict
from visualizer import print_tree


class OrgGraphAnalyzer(object):
    def __init__(self, g):
        self._graph = g
        self._analysis = dict()

    @property
    def analysis(self):
        return self._analysis

    def analyze(self):
        self._analyze_org()
        self._analyze_teams()
        self._analyze_ems()
        self._analyze_ics()

    def _analyze_org(self, team=None):
        # Dont process anything if the team happens to be top level org
        if team and team["name"] == self._graph["org_name"]:
            return

        def edge_selector(edge):
            if team:
                # ensure that both source and destination are connected
                if not self._graph.are_connected(edge["source"], team["name"]):
                    return False

                return True
                
            if edge["type"] != "reports_to":
                return False
            
            return True

        top_key = f"Team `{team['name']}` Stats" if team else "Org Stats"

        g_sub = self._graph.subgraph_edges(
            self._graph.es.select(lambda edge: edge_selector(edge))
        )

        self._analysis[top_key] = {"Reporting": print_tree(g=g_sub, root=0)}

        all_levels = list(set(g_sub.vs["level"]))
        all_regions = list(set(g_sub.vs["geo"]))
        all_genders = list(set(g_sub.vs["gender"]))
        all_roles = list(set(g_sub.vs["role"]))

        # logging.debug(f'All levels: {set(g_sub.vs["level"])}')

        gender_dict = defaultdict(dict)
        level_dict = defaultdict(dict)
        region_dict = defaultdict(dict)
        role_dict = defaultdict(int)

        def vertex_selector(vx):
            v = self._graph.vs(name_eq=vx["name"])[0]
            if not v["type"] == "person":
                return False
            
            if team:
                logging.debug(f"Vertex: {v}, team: {team}")
                logging.debug(f"Are connected: {self._graph.are_connected(v, team)}")
                return self._graph.are_connected(v, team)
            
            return True
        
        people = g_sub.vs.select(lambda v: vertex_selector(v))

        total_in_org = len(people)
        logging.debug(f"Total in org: {total_in_org}")
        self._analysis[top_key]["Total Size"] = total_in_org

        # Level distribution
        for person in people:
            gender = person["gender"]
            level = person["level"]
            geo = person["geo"]
            role = person["role"]

            if level not in level_dict:
                level_dict[level]["total"] = 0
                level_dict[level]["splits"] = defaultdict.fromkeys(all_regions, 0)

            if gender not in gender_dict:
                gender_dict[gender]["total"] = 0
                gender_dict[gender]["splits"] = defaultdict.fromkeys(all_regions, 0)

            if geo not in region_dict:
                region_dict[geo]["total"] = 0
                region_dict[geo]["splits"] = defaultdict.fromkeys(all_levels, 0)

            if role not in role_dict:
                role_dict[role] = 0

            role_dict[role] += 1
            level_dict[level]["total"] += 1
            gender_dict[gender]["total"] += 1
            region_dict[geo]["total"] += 1

            level_dict[level]["splits"][geo] += 1
            gender_dict[gender]["splits"][geo] += 1
            region_dict[geo]["splits"][level] += 1

        level_distribution = [["Level", "Total", "Percentage"]]
        gender_distribution = [["Gender", "Total", "Percentage"]]
        region_distribution = [["Region", "Total", "Percentage"]]

        def percentage(part, whole):
            p = 100 * float(part) / float(whole)
            return str(round(p)) + "%"

        rep_lists = [level_distribution, region_distribution, gender_distribution]
        rep_dicts = [level_dict, region_dict, gender_dict]

        for l, d in zip(rep_lists, rep_dicts):
            logging.debug(
                f'Extending Headers with: {list(d[list(d.keys())[0]]["splits"].keys())}'
            )
            l[0].extend(list(d[list(d.keys())[0]]["splits"].keys()))
            for x in d:
                list_entry = list()
                list_entry.append(x)
                list_entry.append(d[x]["total"])
                list_entry.append(percentage(d[x]["total"], total_in_org))
                logging.debug(f'Values: {list(d[x]["splits"].values())}')
                list_entry.extend(list(d[x]["splits"].values()))
                l.append(list_entry)

        self._analysis[top_key]["Level Distribution"] = level_distribution
        self._analysis[top_key]["Region Distribution"] = region_distribution
        self._analysis[top_key]["Gender Distribution"] = gender_distribution

    def _analyze_ems(self):
        ems = sorted(
            self._graph.vs(role_eq="em"),
            key=lambda x: x.degree(mode="in"),
            reverse=True,
        )
        em_stats = [["EM", "Level", "Teams", "Org Size", "Directs", "Utilization"]]
        for em in ems:
            teams = [a["name"] for a in em.neighbors(mode="out") if a["type"] == "team"]
            directs = em.degree(mode="in")
            utilization = "low" if directs < 5 else "medium" if directs < 9 else "high"
            org_size = len(self._graph.subcomponent(em, mode="in"))
            em_stats.append(
                [em["name"], em["level"], teams, org_size, directs, utilization]
            )
        self._analysis["EM Stats"] = {"Overview": em_stats}

    def _analyze_ics(self):
        ics = sorted(
            self._graph.vs.select(
                lambda vertex: vertex["role"] == "ic"
                and vertex["level"] in self._graph["senior_ic_levels"]
            ),
            key=lambda x: x.degree(mode="in"),
            reverse=True,
        )
        ic_stats = [["IC", "Level", "Areas", "Backing Team"]]
        for ic in ics:
            areas = [a["name"] for a in ic.neighbors(mode="out") if a["type"] == "area"]
            ic_stats.append([ic["name"], ic["level"], areas, 0])
        self._analysis["IC Stats"] = {"Overview": ic_stats}

    def _analyze_teams(self):
        teams = self._graph.vs(type_eq="team")
        for team in teams:
            self._analyze_org(team=team)
