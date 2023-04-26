import igraph as ig
import logging


class OrgGraph(object):
    def __init__(self, yaml_org_model):
        self._org_model = yaml_org_model
        self._members = dict()
        self._teams = dict()
        self._areas = dict()
        self._models = dict()
        self._gen_graph()

    def _gen_graph(self):
        self._parse_members()
        self._parse_teams()
        self._parse_org_models()

    @property
    def members(self):
        return self._members

    @property
    def teams(self):
        return self._teams

    @property
    def areas(self):
        return self._areas

    @property
    def models(self):
        return self._models

    @property
    def senior_ic_levels(self):
        return self._org_model["config"]["senior_ic_levels"]

    @property
    def org_name(self):
        return self._org_model["config"]["org_name"]

    def _parse_members(self):
        ms = self._org_model["members"]["schema"]
        md = self._org_model["members"]["data"]
        cols = [a.rstrip().lstrip() for a in ms.split(",")]
        for row in md:
            rv = [a.rstrip().lstrip() for a in row.split(",")]
            dict_entry = {cols[i]: rv[i] for i in range(len(cols) - 1)}
            # row value can contain additional fields, in which case combine them into the last key of schema
            dict_entry[cols[-1]] = ",".join(rv[len(cols) - 1 :])
            dict_entry["type"] = "person"
            self._members[rv[0]] = dict_entry

    def _parse_teams(self):
        ms = self._org_model["teams"]["schema"]
        md = self._org_model["teams"]["data"]
        cols = [a.rstrip().lstrip() for a in ms.split(",")]
        for row in md:
            rv = [a.rstrip().lstrip() for a in row.split(",")]
            dict_entry = {cols[i]: rv[i] for i in range(len(cols) - 1)}
            # row value can contain additional fields, in which case combine them into the last key of schema
            dict_entry[cols[-1]] = ",".join(rv[len(cols) - 1 :])
            dict_entry["type"] = "team"
            self._teams[rv[0]] = dict_entry

    def _iter_dict(self, d, parent=None, el=[]):
        logging.debug(f"_iter_dict, len(el) = {len(el)}")
        if isinstance(d, dict):
            for k, v in d.items():
                rv = [a.rstrip().lstrip() for a in k.split(",")]
                person = rv[0]
                team = rv[1]
                if person not in self.members:
                    raise ValueError(f"{person} not found in the team members list")

                if team not in self.teams:
                    raise ValueError(f"{team} not found in the team members list")

                # Add entries to areas if not found
                for area in rv[2:]:
                    if area not in self.areas:
                        self._areas[area] = {"name": area, "type": "area"}

                    # Add works_on edges for areas
                    el.append({"source": person, "target": area, "type": "works_on"})

                # Add belongs_to edges for teams
                el.append({"source": person, "target": team, "type": "belongs_to"})

                # Add reports_to edge to parent
                if parent:
                    el.append(
                        {"source": person, "target": parent, "type": "reports_to"}
                    )

                if v:
                    self._iter_dict(v, person, el)
        return el

    def _parse_org_models(self):
        # Recursively iterate org_model dict (model["data"]) to produce edges

        for model in self._org_model["org_models"]:
            model_name = model["name"]
            md = model["data"]
            el = self._iter_dict(md, parent=None, el=[])
            logging.debug(f"Building model for {model_name}")
            logging.debug(f"Length of edge list : {len(el)}")
            vl = list()
            for d in (self.members, self.teams, self.areas):
                vl.extend([d[k] for k in d])
            g = ig.Graph.DictList(vl, el, directed=True)
            g["senior_ic_levels"] = self.senior_ic_levels
            g["org_name"] = self.org_name
            self._models[model_name] = g
