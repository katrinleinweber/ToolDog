#!/usr/bin/env python3

"""
Generation of XML for Galaxy from https://bio.tools based on the Tooldog model using
galaxyxml library.
"""

#  Import  ------------------------------

# General libraries
import os
import copy
import logging

# External libraries
import galaxyxml.tool as gxt
import galaxyxml.tool.parameters as gxtp
from galaxyxml.tool.import_xml import GalaxyXmlParser

# Class and Objects
from .edam_to_galaxy import EdamToGalaxy
from tooldog import __version__

#  Constant(s)  ------------------------------

LOGGER = logging.getLogger(__name__)

#  Class(es)  ------------------------------


class GalaxyToolGen(object):
    """
    Class to support generation of XML from :class:`tooldog.model.Biotool` object.
    """

    def __init__(self, biotool, galaxy_url=None, edam_url=None, mapping_json=None,
                 existing_tool=None):
        """
        Initialize a [Tool] object from galaxyxml with the minimal information
        (a name, an id, a version, a description, the command, the command version
        and a help).

        :param biotool: Biotool object of an entry from https://bio.tools.
        :type biotool: :class:`tooldog.model.Biotool`
        """
        if existing_tool:
            LOGGER.info("Loading existing XML from " + existing_tool)
            gxp = GalaxyXmlParser()
            self.tool = gxp.import_xml(existing_tool)
            # Add information about Tooldog version
            self.tool.add_comment("This tool descriptor has been annotated by ToolDog v" +
                                  __version__)
        else:
            LOGGER.info("Creating new GalaxyToolGen object...")
            # Initialize GalaxyInfo
            self.etog = EdamToGalaxy(galaxy_url=galaxy_url, edam_url=edam_url,
                                     mapping_json=mapping_json)
            # Initialize counters for inputs and outputs
            self.input_ct = 0
            self.output_ct = 0
            # Initialize tool
            #   Get the first sentence of the description only
            description = biotool.description.split('.')[0] + '.'
            self.tool = gxt.Tool(biotool.name, biotool.tool_id, biotool.version,
                                 description, "COMMAND", version_command="COMMAND --version")
            self.tool.help = (biotool.description + "\n\nTool Homepage: " +
                              biotool.homepage)
            #   Add information about Galaxy and EDAM in the XML
            self.tool.add_comment("Information was obtained from the Galaxy instance: " +
                                  self.etog.galaxy_url + " v" +
                                  self.etog.galaxy_version + " and EDAM v" +
                                  self.etog.edam_version)
            # Add information about Tooldog version
            self.tool.add_comment("This tool descriptor has been generated by ToolDog v" +
                                  __version__)

    def add_edam_topic(self, topic):
        """
        Add the EDAM topic to the tool (XML: edam_topics).

        :param topic: Topic object.
        :type topic: :class:`tooldog.model.Topic`
        """
        LOGGER.debug("Adding EDAM topic " + topic.get_edam_id() + " to GalaxyToolGen object.")
        if not hasattr(self.tool, 'edam_topics'):
            # First time we add topics to the tool
            self.tool.edam_topics = gxtp.EdamTopics()
        if not self.tool.edam_topics.has_topic(topic.get_edam_id()):
            self.tool.edam_topics.append(gxtp.EdamTopic(topic.get_edam_id()))

    def add_edam_operation(self, operation):
        """
        Add the EDAM operation to the tool (XML: edam_operations).

        :param topic: Operation object.
        :type topic: :class:`tooldog.model.Operation`
        """
        LOGGER.debug("Adding EDAM operation " + operation.get_edam_id() +
                     " to GalaxyToolGen object.")
        if not hasattr(self.tool, 'edam_operations'):
            # First time we add operations to the tool
            self.tool.edam_operations = gxtp.EdamOperations()
        if not self.tool.edam_operations.has_operation(operation.get_edam_id()):
            self.tool.edam_operations.append(gxtp.EdamOperation(operation.get_edam_id()))

    def add_input_file(self, input_obj):
        """
        Add an input to the tool (XML: <inputs>).

        :param input_obj: Input object.
        :type input_obj: :class:`tooldog.model.Input`
        """
        LOGGER.debug("Adding input to GalaxyToolGen object...")
        if not hasattr(self.tool, 'inputs'):
            self.tool.inputs = gxtp.Inputs()
        # Build parameter
        self.input_ct += 1
        data_uri = input_obj.data_type.get_edam_id()
        # Give unique name to the input
        name = 'INPUT' + str(self.input_ct)
        # Get all different format for this input
        list_formats = []
        if not input_obj.formats:
            list_formats.append(self.etog.get_datatype(edam_data=data_uri))
        else:
            for format_obj in input_obj.formats:
                format_uri = format_obj.get_edam_id()
                list_formats.append(self.etog.get_datatype(edam_data=data_uri,
                                                           edam_format=format_uri))
        formats = ', '.join(list_formats)
        # Create the parameter
        param = gxtp.DataParam(name, label=input_obj.data_type.term,
                               help=input_obj.description, format=formats)
        # Override the corresponding arguments in the command line
        param.command_line_override = '--' + name + ' $' + name
        # Appends parameter to inputs
        self.tool.inputs.append(param)

    def add_output_file(self, output):
        """
        Add an output to the tool (XML: <outputs>).

        :param output: Output object.
        :type output: :class:`tooldog.model.Output`
        """
        LOGGER.debug("Adding output to GalaxyToolGen object...")
        if not hasattr(self.tool, 'outputs'):
            self.tool.outputs = gxtp.Outputs()
        # Build parameter
        self.output_ct += 1
        data_uri = output.data_type.get_edam_id()
        # Give unique name to the output
        name = 'OUTPUT' + str(self.output_ct)
        # Get all different format for this output
        list_formats = []
        if not output.formats:
            list_formats.append(self.etog.get_datatype(edam_data=data_uri))
        else:
            for format_obj in output.formats:
                format_uri = format_obj.get_edam_id()
                list_formats.append(self.etog.get_datatype(edam_data=data_uri,
                                                           edam_format=format_uri))
        formats = ', '.join(list_formats)
        # Create the parameter
        param = gxtp.OutputData(name, format=formats, from_work_dir=name + '.ext')
        param.command_line_override = ''
        self.tool.outputs.append(param)

    def add_citation(self, publication):
        """
        Add publication(s) to the tool (XML: <citations>).

        :param publication: Publication object.
        :type publication: :class:`tooldog.model.Publication`
        """
        LOGGER.debug("Adding citation to GalaxyToolGen object...")
        if not hasattr(self.tool, 'citations'):
            self.tool.citations = gxtp.Citations()
        # Add citation depending the type (doi, pmid...)
        if publication.doi is not None:
            if not self.tool.citations.has_citation('doi', publication.doi):
                self.tool.citations.append(gxtp.Citation('doi', publication.doi))
        # <citation> only supports doi and bibtex as a type
        elif publication.pmid is not None:
            # self.tool.citations.append(gxtp.Citation('pmid', publication.pmid))
            LOGGER.warn('pmid is not supported by <citation>, citation skipped')
        elif publication.pmcid is not None:
            # self.tool.citations.append(gxtp.Citation('pmcid', publication.pmcid))
            LOGGER.warn('pmcid is not supported by <citation>, citation skipped')

    def write_xml(self, out_file=None, index=None, keep_old_command=False):
        """
        Write CWL to STDOUT or out_file(s).

        :param out_file: path to output file.
        :type out_file: STRING
        :param index: Index in case more than one function is described.
        :type index: INT
        """
        # Copy informations to avoid expension of xml in case we write several XMLs
        export_tool = copy.deepcopy(self.tool)
        # Give XML on STDout
        if out_file is None:
            if index is not None:
                print('########## XML number ' + str(index) + ' ##########')
            LOGGER.info("Writing XML file to STDOUT")
            print(export_tool.export(keep_old_command).decode('utf-8'))
        else:
            # Format name for output file(s)
            if index is not None:
                out_file = os.path.splitext(out_file)[0] + str(index) + '.xml'
            else:
                out_file = os.path.splitext(out_file)[0] + '.xml'
            LOGGER.info("Writing XML file to " + out_file)
            with open(out_file, 'w') as file_w:
                file_w.write(export_tool.export(keep_old_command).decode('utf-8'))
