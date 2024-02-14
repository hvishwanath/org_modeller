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
    msg = list()
    toc = list()
    with open(model_file) as f:
        om = yaml.safe_load(f)
        og = OrgGraph(om)
        for k, v in og.models.items():
            header = f"Model Analysis: {k}"
            mod_h = header.lower().replace(" ", "-").replace("`", "")
            
            toc.append(
                f'- [{header}](#{mod_h})'
            )

            msg.append(f"# {header} <a name='{mod_h}'></a>")
            
            #logging.debug(f"Graph ID: {v}")
            # print_msg_box(msg=f"Analyzing model {k}")
            oa = OrgGraphAnalyzer(v)
            oa.analyze()
            for a in oa.analysis:
                a_h = mod_h + a.lower().replace(" ", "-").replace("`", "")
                toc.append(f'  - [{a}](#{a_h})')
                msg.append(f"## {a} <a name='{a_h}'></a>")
                for k, v in oa.analysis[a].items():
                    # k_h = a_h + k.lower().replace(" ", "-").replace("`", "")
                    # msg.append(f"### {k} <a name='{k_h}'></a>")
                    # toc.append(f'    - [{k}](#{k_h})')
                    if isinstance(v, str) or isinstance(v, int):
                        if "Reporting" in k:
                            msg.append(f"```\n{v}\n```")
                        else:
                            msg.append(str(v))
                    else:
                        msg.append(
                            f'\n{pre_b}{tabulate(v, headers="firstrow", tablefmt="github")}{pre_e}\n'
                        )
    print("\n".join(toc))
    print("\n".join(msg))


if "__main__" == __name__:
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.info(f"Starting analysis of {sys.argv[1]}")
    process_org_model(model_file=sys.argv[1])
