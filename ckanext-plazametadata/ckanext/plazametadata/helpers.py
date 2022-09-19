import ckan.plugins.toolkit as toolkit
import logging
import os


PATH = os.path.dirname(os.path.abspath(__file__))


# Reads data from a textFile and converts it to an array
# Used by the vocabulary functions
def get_array_from_file(filename):
    try:
        data_file = open(filename, "r")
        data_array = []
        for data in data_file:
            data_array.append(data.replace("\n", ""))
        data_file.close()
        return data_array
    except:
        return []


# This function return the countries as an array
def get_countries():
    path = os.path.join(PATH, "public/countries.txt")
    return get_array_from_file(path)


# This function returns tags as coma separated strings
def tags_to_string(tags):
    if type(tags) is list:
        tag_string = ""
        for tag in tags:
            tag_string = tag_string + tag + ","
        tag_string = tag_string[: len(tag_string) - 1]

        return tag_string
    else:
        return tags


def tags_to_string_2(tags):
    if type(tags) is list:
        tag_string = ""
        for tag in tags:
            parts = tag.split()
            new_tag = []
            if len(parts) >= 2:
                for i in range(len(parts)):
                    if i == 0:
                        new_tag.append(parts[0])
                    else:
                        if parts[i].find("(") >= 0:
                            new_tag.append(parts[i])
                        else:
                            new_tag.append(parts[i].lower())
                new_tag = " ".join(new_tag)
            else:
                new_tag = tag
            tag_string = tag_string + new_tag + ","
        tag_string = tag_string[: len(tag_string) - 1]

        return tag_string
    else:
        try:
            parts = tags.split()
            new_tag = []
            if len(parts) >= 2:
                for i in range(len(parts)):
                    if i == 0:
                        new_tag.append(parts[0])
                    else:
                        if parts[i].find("(") >= 0:
                            new_tag.append(parts[i])
                        else:
                            new_tag.append(parts[i].lower())
                new_tag = " ".join(new_tag)
            else:
                new_tag = tags

            return new_tag
        except:
            return tags


# This function removes unhandled characters from the list of tags
def fix_tag(tag):
    res = tag
    res = res.replace(",", "_")
    res = res.replace("'", "")
    res = res.replace('"', "")
    res = res.replace("(", "")
    res = res.replace(")", "")
    return res


# This function creates a vocabulary using a text file
def create_vocab(vocabulary, list_file):
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
    context = {"user": user["name"]}

    try:
        data = {"id": vocabulary}
        voc = toolkit.get_action("vocabulary_show")(context, data)
        print(
            "Vocabulary {0} already exists, Adding terms from {1}".format(
                vocabulary, list_file
            )
        )
        for tag in get_array_from_file(list_file):
            print("Adding tag {0} to vocab '{1}'".format(tag, voc["id"]))
            try:
                data = {
                    "name": fix_tag(tag),
                    "vocabulary_id": voc["id"],
                    "display_name": tag,
                }
                toolkit.get_action("tag_create")(context, data)
            except Exception as e:
                print(
                    "Error {0}: while adding tag {1} in vocab '{2}' Skipping it.".format(
                        e.message, tag, voc["id"]
                    )
                )
    except toolkit.ObjectNotFound:
        print("Creating vocab '{0}'".format(vocabulary))
        data = {"name": vocabulary}
        vocab = toolkit.get_action("vocabulary_create")(context, data)
        for tag in get_array_from_file(list_file):
            logging.info("Adding tag {0} to vocab '{1}'".format(tag, vocabulary))
            data = {
                "name": fix_tag(tag),
                "vocabulary_id": vocab["id"],
                "display_name": tag,
            }
            toolkit.get_action("tag_create")(context, data)
    return True


# This Helper function checks if a vocabulary exists
def vocabulary_exists(vocabulary):
    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
    context = {"user": user["name"]}
    try:
        data = {"id": vocabulary}
        toolkit.get_action("vocabulary_show")(context, data)
        return True
    except toolkit.ObjectNotFound:
        return False


# This Helper function creates the countries vocabulary from a text file
def create_countries_vocab():
    path = os.path.join(PATH, "public/countries.txt")
    return create_vocab("plaza_voc_countries", path)


def delete_vocab(voc_name, voc_list_file):

    user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
    context = {"user": user["name"]}

    data = {"id": voc_name}

    for tag in get_array_from_file(voc_list_file):
        data = {"id": fix_tag(tag), "vocabulary_id": voc_name}
        try:
            toolkit.get_action("tag_delete")(context, data)
            logging.info("Tag {0} deleted".format(tag))
        except:
            print("Tag " + tag + " Does not exists")

    toolkit.get_action("vocabulary_delete")(context, data)
    print(voc_name + " vocabulary deleted.")
