import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from .helpers import create_countries_vocab, get_countries, tags_to_string, vocabulary_exists


class PlazametadataPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IFacets)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer # This adds new directories into CKAN
    # The most important here is templates. It is used to add new templates or to overwrite or extend current templates
    # For example:
    # In the code of CKAN you have:
    #       templates
    #         |-home
    #             |-snippets
    #                 |-search.html
    # In this plugin we have:
    #       templates
    #         |-home
    #             |-snippets
    #                 |-search.html
    # This means that our plugin is overwriting or modifying the file search.html

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("fanstatic", "plazametadata")

    # -------------------------------End of IConfigurer -----------------------------------

    # ITemplateHelpers # This adds new functions that we can use in templates

    def get_helpers(self):
        return {
            "plaza_create_countries_vocab": create_countries_vocab,
            "plaza_get_countries": get_countries,
            "plaza_tags_to_string": tags_to_string,
            "plaza_vocabulary_exists": vocabulary_exists,
        }

    # -------------------------------End of ITemplateHelpers -----------------------------------

    # IDatasetForm # This adds new fields in the metadata of a dataset. For example countries
    # CKAN can store extra fields in two ways: tags or extras

    def _add_custom_metadata_to_schema(self, schema):
        """
        This function adds custom fields to the dataset schema.
        Used by:
            create_package_schema(): When CKAN creates a dataset
            update_package_schema(): When CKAN updates a dataset
        :param schema: The dataset schema
        :return: A modified version of the schema
        """

        # Add plaza_country to the schema. STORE it in tags with a controlled vocabulary called plaza_voc_countries
        schema.update(
            {
                "plaza_country": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_tags")("plaza_voc_countries"),
                ]
            },
        )
        # Add plaza_creator_orcid to the schema. STORE it in extras
        schema.update(
            {
                "plaza_creator_orcid": [
                    toolkit.get_validator("ignore_missing"),
                    toolkit.get_converter("convert_to_extras"),
                ]
            }
        )
        return schema

    def create_package_schema(self):
        """
        This function is called by CKAN when creating a dataset.
        We add the new fields to the schema
        :return: A modified version of the schema
        """
        schema = super(PlazametadataPlugin, self).create_package_schema()
        schema = self._add_custom_metadata_to_schema(schema)
        return schema

    def update_package_schema(self):
        """
        This function is called by CKAN when updates a dataset.
        We add the new fields to the schema
        :return: A modified version of the schema
        """
        schema = super(PlazametadataPlugin, self).update_package_schema()
        schema = self._add_custom_metadata_to_schema(schema)
        return schema

    def show_package_schema(self):
        """
        This function is called by CKAN when loading the metadata of a dataset
        We add the new fields to the schema.
        :return: A modified version of the schema
        """
        schema = super(PlazametadataPlugin, self).show_package_schema()
        schema["tags"]["__extras"].append(toolkit.get_converter("free_tags_only"))

        # Add plaza_country to the schema. LOAD it from tags with a controlled vocabulary called plaza_voc_countries
        schema.update(
            {
                "plaza_country": [
                    toolkit.get_converter("convert_from_tags")("plaza_voc_countries"),
                    toolkit.get_validator("ignore_missing"),
                ]
            }
        )

        # Add plaza_creator_orcid to the schema. LOAD it from extras
        schema.update(
            {
                "plaza_creator_orcid": [
                    toolkit.get_converter("convert_from_extras"),
                    toolkit.get_validator("ignore_missing"),
                ]
            }
        )
        return schema

    # The following secondary functions of IDatasetForm are implemented to satisfy the plugin. Not important

    # These record how many times methods that this plugin's methods are
    # called, for testing purposes.
    num_times_new_template_called = 0
    num_times_read_template_called = 0
    num_times_edit_template_called = 0
    num_times_search_template_called = 0
    num_times_history_template_called = 0
    num_times_package_form_called = 0
    num_times_check_data_dict_called = 0
    num_times_setup_template_variables_called = 0

    def setup_template_variables(self, context, data_dict):
        PlazametadataPlugin.num_times_setup_template_variables_called += 1
        return super(PlazametadataPlugin, self).setup_template_variables(
            context, data_dict
        )

    def new_template(self):
        PlazametadataPlugin.num_times_new_template_called += 1
        return super(PlazametadataPlugin, self).new_template()

    def read_template(self):
        PlazametadataPlugin.num_times_read_template_called += 1
        return super(PlazametadataPlugin, self).read_template()

    def edit_template(self):
        PlazametadataPlugin.num_times_edit_template_called += 1
        return super(PlazametadataPlugin, self).edit_template()

    def search_template(self):
        PlazametadataPlugin.num_times_search_template_called += 1
        return super(PlazametadataPlugin, self).search_template()

    def history_template(self):
        PlazametadataPlugin.num_times_history_template_called += 1
        return super(PlazametadataPlugin, self).history_template()

    def package_form(self):
        PlazametadataPlugin.num_times_package_form_called += 1
        return super(PlazametadataPlugin, self).package_form()

    def check_data_dict(self, data_dict, schema=None):
        PlazametadataPlugin.num_times_check_data_dict_called += 1

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []

    # ----------------------End of IDatasetForm  -------------------------------------------------

    # IFacets # This adds new vocabularies to the Facets so users can slice datasets

    def dataset_facets(self, facets_dict, package_type):
        facets_dict["vocab_plaza_voc_countries"] = "Countries"
        return facets_dict

    def group_facets(self, facets_dict, group_type, package_type):
        facets_dict["vocab_plaza_voc_countries"] = "Countries"
        return facets_dict

    def organization_facets(self, facets_dict, organization_type, package_type):
        facets_dict["vocab_plaza_voc_countries"] = "Countries"
        return facets_dict

    # -------------------------------End of IFacets -----------------------------------
