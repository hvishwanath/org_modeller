import yaml
import sys
import os
import logging

from tabulate import tabulate, PRESERVE_WHITESPACE
from org_graph import OrgGraph
from org_analyzer import OrgGraphAnalyzer
from visualizer import print_msg_box, print_tree

PRESERVE_WHITESPACE = True


def process_org_model(model_file):
    pre_b = ""
    pre_e = ""
    with open(model_file) as f:
        om = yaml.safe_load(f)
        og = OrgGraph(om)
        for k, v in og.models.items():
            print(f"# Model Analysis: {k}")
            logging.debug(f"Graph ID: {v}")
            # print_msg_box(msg=f"Analyzing model {k}")
            oa = OrgGraphAnalyzer(v)
            oa.analyze()
            for a in oa.analysis:
                print(f"## {a}")
                for k, v in oa.analysis[a].items():
                    print(f"### {k}")
                    if isinstance(v, str) or isinstance(v, int):
                        if "Reporting" in k:
                            print(f"```\n{v}\n```")
                        else:
                            print(v)
                    else:
                        print(
                            f'\n{pre_b}{tabulate(v, headers="firstrow", tablefmt="github")}{pre_e}\n'
                        )


if "__main__" == __name__:
    logging.basicConfig(stream=sys.stdout, level=logging.ERROR)
    logging.info(f"Starting analysis of {sys.argv[1]}")
    process_org_model(model_file=sys.argv[1])
