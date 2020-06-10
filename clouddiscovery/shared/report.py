from typing import List

import os
import base64

from shared.common import Resource, ResourceEdge, message_handler
from shared.error_handler import exception

from jinja2 import Environment, FileSystemLoader

PATH_REPORT_HTML_OUTPUT = "./assets/html_report/"
PATH_DIAGRAM_OUTPUT = "./assets/diagrams/"


class Report(object):
    @staticmethod
    def make_directories():
        # Check if assets/diagram directory exists
        if not os.path.isdir(PATH_DIAGRAM_OUTPUT):
            try:
                os.mkdir(PATH_DIAGRAM_OUTPUT)
            except OSError:
                print("Creation of the directory %s failed \n" % PATH_DIAGRAM_OUTPUT)
            else:
                print("Successfully created the directory %s \n" % PATH_DIAGRAM_OUTPUT)

    @exception
    def general_report(
        self, resources: List[Resource], resource_relations: List[ResourceEdge]
    ):

        message_handler("\n\nFound resources", "HEADER")

        for resource in resources:
            message = "resource type: {} - resource id: {} - resource name: {} - resource details: {}".format(
                resource.digest.type,
                resource.digest.id,
                resource.name,
                resource.details,
            )

            message_handler(message, "OKBLUE")

        message_handler("\n\nFound relations", "HEADER")
        for resource_relation in resource_relations:
            message = "resource type: {} - resource id: {} -> resource type: {} - resource id: {}".format(
                resource_relation.from_node.type,
                resource_relation.from_node.id,
                resource_relation.to_node.type,
                resource_relation.to_node.id,
            )

            message_handler(message, "OKBLUE")

    @exception
    def html_report(
        self,
        resources: List[Resource],
        resource_relations: List[ResourceEdge],
        default_name: str,
        diagram_name: str,
    ):
        dir_template = Environment(
            loader=FileSystemLoader(
                os.path.dirname(os.path.abspath(__file__)) + "/../templates/"
            ),
            trim_blocks=True,
        )

        """generate image64 to add to report"""
        diagram_image = None
        if diagram_name is not None:
            image_name = PATH_DIAGRAM_OUTPUT + diagram_name + ".png"
            with open(image_name, "rb") as image_file:
                diagram_image = base64.b64encode(image_file.read()).decode("utf-8")

        html_output = dir_template.get_template("report_html.html").render(
            default_name=default_name,
            resources_found=resources,
            resources_relations=resource_relations,
            diagram_image=diagram_image,
        )

        self.make_directories()

        name_output = PATH_REPORT_HTML_OUTPUT + default_name + ".html"

        with open(name_output, "w") as file_output:
            file_output.write(html_output)

        message_handler("\n\nHTML report generated", "HEADER")
        message_handler("Check your HTML report: " + name_output, "OKBLUE")
