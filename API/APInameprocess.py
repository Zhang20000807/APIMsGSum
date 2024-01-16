import pickle
import re
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer


# 如果没有安装过nltk的data需要先下载
# nltk.download('averaged_perceptron_tagger')
# nltk.download('punkt')
# nltk.download('wordnet')


# 函数将NLTK的词性标注转换为WordNet的标签，以便进行词形还原
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def pos_tagging(words):
    """
    Perform POS tagging on a list of words, and then lemmatize them.

    Parameters:
    words (List[str]): A list of words to be POS tagged.

    Returns:
    List[Tuple[str, str]]: A list of tuples, where each tuple contains a word and its POS tag.
    """
    # 进行基本的词性标注
    tagged_words = nltk.pos_tag(words)

    # 基于上下文进行词形还原
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = []
    for word, tag in tagged_words:
        wntag = get_wordnet_pos(tag)
        if wntag is None:
            # 如果没有对应的WordNet词性标签，保留原始词形
            lemma = word
        else:
            # 否则，进行词形还原
            lemma = lemmatizer.lemmatize(word, pos=wntag)
        lemmatized_words.append((lemma, tag))

    return lemmatized_words


def split_camelcase(word):
    # 分割驼峰式命名
    return re.findall(r'([A-Z]?[a-z]+|[A-Z]+(?![a-z]))', word)


def split_snakecase(word):
    # 分割下划线命名
    return word.split('_')


# 定义启发式规则
def parse_api_name(api_name, tags):
    pattern = ""
    sp_words = []
    for word, tag in tags:
        # 动词
        if tag.startswith('VB') or tag == 'MD':
            pattern += "verb "
            sp_words.append(word)
        # 名词
        elif tag.startswith('NN'):
            pattern += "noun "
            sp_words.append(word)
        # 形容词
        elif tag.startswith('JJ') or tag == 'RB' or tag == 'RBR' or tag == 'RBS':
            pattern += "adjective "
            sp_words.append(word)
        # 介词或连词
        elif tag == 'IN' or tag == 'TO':
            pattern += "preposition "
            sp_words.append(word)
        # 限定词如 "all", "each"
        elif tag == 'DT':
            pattern += "determiner "
            sp_words.append(word)
        # 小品词如 "out" 或 "up"
        elif tag == 'RP':
            pattern += "particle "
            sp_words.append(word)
        # 并列连词如 "and", "or", "but", "either"
        elif tag == 'CC':
            pattern += "conjunction "
            sp_words.append(word)
        # 数词如 "one", "two", "first", "second"
        elif tag == 'CD':
            pattern += "number "
            sp_words.append(word)
        # 疑问副词如 "when", "where", "why"
        elif tag == 'WRB':
            pattern += "wh-adverb "
            sp_words.append(word)
        else:
            pattern += "unknown(" + tag + ") "
            sp_words.append(word)

    # 去掉尾部空格，并转换为小写
    pattern = pattern.strip().lower()
    # return pattern
    # 根据得到的模式返回结果
    if pattern == "verb noun":
        # Assuming sp_words = ["create", "session"]
        description = sp_words[0] + " a " + sp_words[1]  # "create a session"
        return_type = "the created " + sp_words[1]  # "the created session"
    elif pattern == "noun verb":
        # Assuming sp_words = ["file", "upload"]
        description = "perform " + sp_words[1] + " on the " + sp_words[0]  # "perform upload on the file"
        return_type = "confirmation of the " + sp_words[1]  # "confirmation of the upload"
    elif pattern == "verb adjective noun":
        # Assuming sp_words = ["make", "public", "profile"]
        description = sp_words[0] + " the " + sp_words[2] + " " + sp_words[1]  # "make the profile public"
        return_type = "status indicating if the " + sp_words[2] + " is now " + sp_words[
            1]  # "status indicating if the profile is now public"
    elif pattern == "adjective noun":
        # Assuming sp_words = ["active", "user"]
        description = "get the " + sp_words[1] + " that is " + sp_words[0]  # "get the user that is active"
        return_type = "list of " + sp_words[0] + " " + sp_words[1] + "s"  # "list of active users"
    elif pattern == "verb":
        # Assuming sp_words = ["authenticate"]
        description = "perform the " + sp_words[0] + " action"  # "perform the authenticate action"
        return_type = "result of the " + sp_words[0]  # "result of the authenticate"
    elif pattern == "noun":
        # Assuming sp_words = ["invoice"]
        description = "retrieve the " + sp_words[0]  # "retrieve the invoice"
        return_type = "the requested " + sp_words[0]  # "the requested invoice"
    elif pattern == "noun noun":
        # Assuming sp_words = ["user", "profile"]
        description = "get the " + sp_words[1] + " for the " + sp_words[0]  # "get the profile for the user"
        return_type = "the " + sp_words[0] + "'s " + sp_words[1]  # "the user's profile"
    elif pattern == "verb noun verb":
        # Assuming sp_words = ["create", "invoice", "send"]
        description = sp_words[0] + " a " + sp_words[1] + " and then " + sp_words[
            2] + " it"  # "create an invoice and then send it"
        return_type = "outcome of the " + sp_words[2]  # "outcome of the send"
    elif pattern == "noun noun noun":
        # Assuming sp_words = ["customer", "order", "detail"]
        description = "retrieve the " + sp_words[2] + " for the " + sp_words[1] + " of the " + sp_words[
            0]  # "retrieve the detail for the order of the customer"
        return_type = "detailed information about the " + sp_words[1]  # "detailed information about the order"
    elif pattern == "verb noun noun":
        # Assuming sp_words = ["assign", "role", "user"]
        description = sp_words[0] + " a " + sp_words[1] + " to the " + sp_words[2]  # "assign a role to the user"
        return_type = "confirmation of the " + sp_words[1] + " assignment"  # "confirmation of the role assignment"
    elif pattern == "verb adjective noun noun":
        # Assuming sp_words = ["set", "default", "user", "role"]
        description = sp_words[0] + " the " + sp_words[2] + "'s " + sp_words[3] + " to " + sp_words[
            1]  # "set the user's role to default"
        return_type = "status that the " + sp_words[3] + " has been " + sp_words[
            1]  # "status that the role has been default"
    elif pattern == "verb verb noun":
        # Assuming sp_words = ["start", "monitor", "service"]
        description = sp_words[0] + " and " + sp_words[1] + " the " + sp_words[2]  # "start and monitor the service"
        return_type = "the status of " + sp_words[2] + " operation"  # "the status of service operation"
    elif pattern == "adjective noun noun":
        # Assuming sp_words = ["recent", "user", "activity"]
        description = "get " + sp_words[0] + " " + sp_words[2] + " for the " + sp_words[
            1]  # "get recent activity for the user"
        return_type = "list of " + sp_words[0] + " " + sp_words[1] + " " + sp_words[
            2] + "s"  # "list of recent user activities"
    elif pattern == "noun verb noun":
        # Assuming sp_words = ["system", "log", "error"]
        description = "use the " + sp_words[0] + " to " + sp_words[1] + " the " + sp_words[
            2]  # "use the system to log the error"
        return_type = "record of the logged " + sp_words[2]  # "record of the logged error"
    elif pattern == "verb noun noun noun":
        # Assuming sp_words = ["map", "user", "permission", "group"]
        description = sp_words[0] + " the " + sp_words[1] + " to a " + sp_words[3] + " with " + sp_words[
            2]  # "map the user to a group with permission"
        return_type = "result of the " + sp_words[1] + " mapping"  # "result of the user mapping"
    elif pattern == "noun noun noun noun":
        # Assuming sp_words = ["product", "sales", "report", "monthly"]
        description = "generate the " + sp_words[3] + " " + sp_words[2] + " for " + sp_words[1] + " of " + sp_words[
            0]  # "generate the monthly report for sales of product"
        return_type = "the " + sp_words[3] + " " + sp_words[2] + " content"  # "the monthly report content"
    elif pattern == "verb adjective":
        # Assuming sp_words = ["make", "editable"]
        description = sp_words[0] + " something to be " + sp_words[1]  # "make something to be editable"
        return_type = "status after making it " + sp_words[1]  # "status after making it editable"
    elif pattern == "noun adjective":
        description = "get a " + sp_words[1] + " " + sp_words[0]
        return_type = "Returns a " + sp_words[1] + " " + sp_words[0]
    elif pattern == "verb noun preposition noun":
        description = sp_words[0] + " a " + sp_words[1] + " for a " + sp_words[3]
        return_type = "Results of the " + sp_words[0] + " action"
    elif pattern == "verb adjective noun noun noun":
        description = sp_words[0] + " a " + sp_words[4] + " that has a " + sp_words[1] + " " + sp_words[2] + " and " + \
                      sp_words[3]
        return_type = "The updated " + sp_words[4] + " details"
    elif pattern == "noun preposition noun":
        description = "get a " + sp_words[0] + " for a " + sp_words[2]
        return_type = "The " + sp_words[0] + " details for the given " + sp_words[2]
    elif pattern == "noun adjective noun noun":
        description = "get a " + sp_words[3] + " that is a " + sp_words[1] + " " + sp_words[0] + " and has " + sp_words[
            2]
        return_type = "The " + sp_words[3] + " details"
    elif pattern == "verb noun preposition":
        description = sp_words[0] + " the " + sp_words[1] + " " + sp_words[2]
        return_type = "The result of the " + sp_words[0] + " operation"
    elif pattern == "verb verb":
        description = sp_words[0] + " and then " + sp_words[1]
        return_type = "The outcome after " + sp_words[0] + " and " + sp_words[1] + " actions"
    elif pattern == "noun noun verb":
        description = "get a " + sp_words[2] + " related to both " + sp_words[0] + " and " + sp_words[1]
        return_type = "The " + sp_words[2] + " related to the " + sp_words[0] + " and " + sp_words[1]
    elif pattern == "noun adjective noun":
        description = "get a " + sp_words[2] + " that is a " + sp_words[1] + " " + sp_words[0]
        return_type = "The " + sp_words[2] + " that is " + sp_words[1] + " " + sp_words[0]
    elif pattern == "preposition noun":
        description = "execute " + sp_words[1] + " " + sp_words[0]
        return_type = "The outcome of the execution"
    elif pattern == "verb adjective noun noun noun":
        description = sp_words[0] + " a " + sp_words[2] + " that is " + sp_words[1] + " and related to " + sp_words[
            3] + " and " + sp_words[4]
        return_type = "The modified " + sp_words[2]
    elif pattern == "noun preposition":
        description = "associate the " + sp_words[0] + " with " + sp_words[1]
        return_type = "Association status of the " + sp_words[0]
    elif pattern == "verb adjective adjective noun":
        description = sp_words[0] + " a " + sp_words[3] + " that is " + sp_words[1] + " and " + sp_words[2]
        return_type = "The " + sp_words[3] + " after the update"
    elif pattern == "adjective adjective noun":
        description = "get a " + sp_words[2] + " that is both " + sp_words[0] + " and " + sp_words[1]
        return_type = "A " + sp_words[2] + " that matches the criteria"
    elif pattern == "verb noun adjective":
        description = sp_words[0] + " a " + sp_words[1] + " that is " + sp_words[2]
        return_type = "Returns a " + sp_words[1] + " that is " + sp_words[2]
    elif pattern == "adjective":
        description = "make it " + sp_words[0]
        return_type = "Indicates a state change to " + sp_words[0]
    elif pattern == "noun noun noun verb":
        description = "get a " + sp_words[3] + " related to " + sp_words[0] + ", " + sp_words[1] + " and " + sp_words[2]
        return_type = "Returns a " + sp_words[3] + " with relations to specified entities"
    elif pattern == "verb adjective adjective":
        description = sp_words[0] + " something to be " + sp_words[1] + " and " + sp_words[2]
        return_type = "Results in an updated state that is both " + sp_words[1] + " and " + sp_words[2]
    elif pattern == "preposition adjective noun":
        description = "for a " + sp_words[2] + " that is " + sp_words[1]
        return_type = "Returns a " + sp_words[2] + " that is " + sp_words[1]
    elif pattern == "noun verb noun noun":
        description = "use the " + sp_words[0] + " to " + sp_words[1] + " the " + sp_words[2] + " and " + sp_words[3]
        return_type = "Results from using the " + sp_words[0] + " to " + sp_words[1]
    elif pattern == "preposition verb noun":
        description = "proceed to " + sp_words[1] + " the " + sp_words[2] + " " + sp_words[0]
        return_type = "Results of the action to " + sp_words[1] + " the " + sp_words[2]
    elif pattern == "verb preposition noun":
        description = sp_words[0] + " towards " + sp_words[2] + " using " + sp_words[1]
        return_type = "The outcome of " + sp_words[0] + "ing towards " + sp_words[2]
    elif pattern == "adjective noun noun noun":
        description = "get a " + sp_words[0] + " " + sp_words[1] + " with related " + sp_words[2] + " and " + sp_words[
            3]
        return_type = "Returns a " + sp_words[0] + " " + sp_words[1] + " with respective relations"
    elif pattern == "preposition verb":
        description = "initiate an action to " + sp_words[1] + " " + sp_words[0]
        return_type = "Initiates an action and returns its result"
    elif pattern == "noun verb adjective noun":
        description = "use the " + sp_words[0] + " to " + sp_words[1] + " a " + sp_words[3] + " that is " + sp_words[2]
        return_type = "Uses the " + sp_words[0] + " to obtain a modified " + sp_words[3]
    elif pattern == "verb noun verb noun":
        description = sp_words[0] + " the " + sp_words[1] + " and then " + sp_words[2] + " the " + sp_words[3]
        return_type = "Performs two operations and returns the final result"
    elif pattern == "verb adjective noun verb":
        description = sp_words[0] + " a " + sp_words[2] + " to be " + sp_words[1] + " and then " + sp_words[3] + " it"
        return_type = "Alters a " + sp_words[2] + " and applies the " + sp_words[3] + " operation"
    elif pattern == "verb adjective adjective noun noun":
        description = sp_words[0] + " a " + sp_words[4] + " that is both " + sp_words[1] + " and " + sp_words[
            2] + ", relating to " + sp_words[3]
        return_type = "Updates a " + sp_words[4] + " and associates it with " + sp_words[3]
    elif pattern == "verb verb adjective":
        description = sp_words[0] + ", then " + sp_words[1] + " and ensure it is " + sp_words[2]
        return_type = "Ensures the result is " + sp_words[2] + " after " + sp_words[0] + " and " + sp_words[1]
    elif pattern == "verb verb noun noun":
        description = sp_words[0] + " and " + sp_words[1] + " related to the " + sp_words[2] + " and " + sp_words[3]
        return_type = "Perform actions " + sp_words[0] + " and " + sp_words[1] + " and return the result for " + \
                      sp_words[2] + " and " + sp_words[3]
    elif pattern == "verb noun adjective noun":
        description = sp_words[0] + " a " + sp_words[1] + " that is " + sp_words[2] + " relating to " + sp_words[3]
        return_type = "Returns a " + sp_words[2] + " " + sp_words[1] + " related to " + sp_words[3]
    elif pattern == "verb noun preposition verb":
        description = sp_words[0] + " a " + sp_words[1] + " to " + sp_words[3] + " it " + sp_words[2]
        return_type = "Perform " + sp_words[0] + " operation and " + sp_words[3] + " on " + sp_words[1]
    elif pattern == "noun noun preposition noun":
        description = "retrieve " + sp_words[0] + " and " + sp_words[1] + " for the " + sp_words[3] + " " + sp_words[2]
        return_type = "Returns " + sp_words[0] + " and " + sp_words[1] + " associated with " + sp_words[3]
    elif pattern == "adjective verb noun":
        description = "perform a/an " + sp_words[1] + " on the " + sp_words[2] + " that is " + sp_words[0]
        return_type = "Performs the action and returns the appropriately " + sp_words[0] + " " + sp_words[2]
    elif pattern == "adjective noun verb":
        description = "retrieve a " + sp_words[0] + " " + sp_words[1] + " and then " + sp_words[2] + " it"
        return_type = "Returns and then " + sp_words[2] + "s a/an " + sp_words[0] + " " + sp_words[1]
    elif pattern == "verb determiner noun":
        description = sp_words[0] + " the specified " + sp_words[2] + " with " + sp_words[1]
        return_type = "Applies the " + sp_words[0] + " operation to the given " + sp_words[2]
    elif pattern == "noun noun noun noun noun":
        description = "retrieve a complex structure involving " + sp_words[0] + ", " + sp_words[1] + ", " + sp_words[
            2] + ", " + sp_words[3] + ", and " + sp_words[4]
        return_type = "Returns a structure combining " + sp_words[0] + ", " + sp_words[1] + ", " + sp_words[2] + ", " + \
                      sp_words[3] + ", and " + sp_words[4]
    elif pattern == "noun preposition verb":
        description = sp_words[0] + " with an action to " + sp_words[2] + " " + sp_words[1]
        return_type = "Performs " + sp_words[2] + " related to " + sp_words[0]
    elif pattern == "preposition noun noun":
        description = "concerning the " + sp_words[1] + " and " + sp_words[2]
        return_type = "Relates to the " + sp_words[1] + " and " + sp_words[2]
    elif pattern == "verb verb adjective noun":
        description = sp_words[0] + ", then " + sp_words[1] + " a " + sp_words[3] + " to be " + sp_words[2]
        return_type = "Performs " + sp_words[0] + " and " + sp_words[1] + ", resulting in a/an " + sp_words[2] + " " + \
                      sp_words[3]
    elif pattern == "verb determiner":
        description = sp_words[0] + " this specific item"
        return_type = "Applies " + sp_words[0] + " to the specified item"
    elif pattern == "verb noun noun verb":
        description = sp_words[0] + " the " + sp_words[1] + " with " + sp_words[2] + " and then " + sp_words[3] + " it"
        return_type = "Modifies and processes the " + sp_words[1] + " and returns the result"
    elif pattern == "noun preposition verb noun":
        description = "link the " + sp_words[0] + " with " + sp_words[3] + " through the action of " + sp_words[2]
        return_type = "Creates an association between " + sp_words[0] + " and " + sp_words[3] + " via " + sp_words[2]
    elif pattern == "noun noun preposition verb":
        description = "connect " + sp_words[0] + " and " + sp_words[1] + " by performing " + sp_words[
            3] + " in the context of " + sp_words[2]
        return_type = "Forms a relationship between " + sp_words[0] + " and " + sp_words[
            1] + " through the action of " + sp_words[3]
    elif pattern == "adjective adjective noun noun":
        description = "get " + sp_words[2] + " and " + sp_words[3] + " that are both " + sp_words[0] + " and " + \
                      sp_words[1]
        return_type = "Returns " + sp_words[2] + " and " + sp_words[3] + " with qualities " + sp_words[0] + " and " + \
                      sp_words[1]
    elif pattern == "noun determiner":
        description = "get the specified " + sp_words[0]
        return_type = "Returns the particular " + sp_words[0] + " mentioned"
    elif pattern == "verb adjective noun preposition noun":
        description = sp_words[0] + " a " + sp_words[1] + " " + sp_words[2] + " in relation to " + sp_words[4] + " " + \
                      sp_words[3]
        return_type = "Modifies a " + sp_words[2] + " in a " + sp_words[1] + " manner concerning " + sp_words[4]
    elif pattern == "noun noun adjective noun":
        description = "obtain a " + sp_words[3] + " associated with " + sp_words[0] + " and " + sp_words[
            1] + " that is " + sp_words[2]
        return_type = "Returns a " + sp_words[3] + " connected to " + sp_words[0] + " and " + sp_words[
            1] + " with attribute " + sp_words[2]
    elif pattern == "noun verb adjective":
        description = sp_words[1] + " using the " + sp_words[0] + " to become " + sp_words[2]
        return_type = "Utilizes the " + sp_words[0] + " to achieve a " + sp_words[2] + " state"
    elif pattern == "preposition":
        description = "involve action with respect to " + sp_words[0]
        return_type = "Returns the result of involving action with respect to " + sp_words[0]
    elif pattern == "adjective adjective":
        description = "make it both " + sp_words[0] + " and " + sp_words[1]
        return_type = "Returns status after making it " + sp_words[0] + " and " + sp_words[1]
    elif pattern == "verb preposition verb":
        description = sp_words[0] + " and then " + sp_words[2] + " through " + sp_words[1]
        return_type = "Performs " + sp_words[0] + " and then " + sp_words[2] + " through " + sp_words[1]
    elif pattern == "verb preposition":
        description = sp_words[0] + " towards " + sp_words[1]
        return_type = "Initiates " + sp_words[0] + " towards " + sp_words[1]
    elif pattern == "verb particle noun":
        description = sp_words[0] + " the " + sp_words[2] + " using " + sp_words[1]
        return_type = "Applies " + sp_words[0] + " to " + sp_words[2] + " using " + sp_words[1]
    elif pattern == "noun noun adjective":
        description = "get a " + sp_words[0] + " and " + sp_words[1] + " that is " + sp_words[2]
        return_type = "Retrieves a " + sp_words[2] + " result related to " + sp_words[0] + " and " + sp_words[1]
    elif pattern == "verb adjective verb noun":
        description = sp_words[0] + " and " + sp_words[2] + " a " + sp_words[3] + " that is " + sp_words[1]
        return_type = "Applies " + sp_words[0] + " and " + sp_words[2] + " to achieve a " + sp_words[1] + " " + \
                      sp_words[3]
    elif pattern == "conjunction noun":
        description = "combine with the " + sp_words[1]
        return_type = "Combines with the " + sp_words[1]
    elif pattern == "verb number noun":
        description = sp_words[0] + " the " + sp_words[2] + " in the amount of " + sp_words[1]
        return_type = "Performs " + sp_words[0] + " on " + sp_words[2] + " in specified quantity"
    elif pattern == "adjective noun preposition noun":
        description = "get a " + sp_words[1] + " that is " + sp_words[0] + " in relation to " + sp_words[3]
        return_type = "Returns a " + sp_words[0] + " " + sp_words[1] + " in relation to " + sp_words[3]
    elif pattern == "noun noun preposition":
        description = "connect " + sp_words[0] + " with " + sp_words[1] + " via " + sp_words[2]
        return_type = "Creates a connection between " + sp_words[0] + " and " + sp_words[1] + " via " + sp_words[2]
    elif pattern == "verb verb verb":
        description = sp_words[0] + ", " + sp_words[1] + ", and then " + sp_words[2]
        return_type = "Executes a sequence of actions: " + sp_words[0] + ", " + sp_words[1] + ", " + sp_words[2]
    elif pattern == "noun verb adjective noun noun":
        description = "use the " + sp_words[0] + " to " + sp_words[1] + " a " + sp_words[3] + " " + sp_words[
            4] + " that is " + sp_words[2]
        return_type = "Uses " + sp_words[0] + " to " + sp_words[1] + " and obtain a " + sp_words[2] + " " + sp_words[
            3] + " " + sp_words[4]
    elif pattern == "verb adjective verb":
        description = sp_words[0] + " in a " + sp_words[1] + " manner and then " + sp_words[2]
        return_type = "Performs " + sp_words[0] + " and " + sp_words[2] + " in a " + sp_words[1] + " way"
    elif pattern == "noun preposition adjective noun":
        description = sp_words[0] + " with a " + sp_words[3] + " that is " + sp_words[2]
        return_type = "Associates " + sp_words[0] + " with a " + sp_words[2] + " " + sp_words[3]
    elif pattern == "verb adjective preposition":
        description = sp_words[0] + " in a way that is " + sp_words[1] + " " + sp_words[2]
        return_type = sp_words[0] + " with the quality of being " + sp_words[1]
    elif pattern == "noun conjunction noun":
        description = sp_words[0] + " combined with " + sp_words[2]
        return_type = "Combination of " + sp_words[0] + " and " + sp_words[2]
    elif pattern == "adjective verb":
        description = "act to be " + sp_words[0] + " and then " + sp_words[1]
        return_type = "Action resulting in a state that is " + sp_words[0]
    elif pattern == "noun verb verb":
        description = sp_words[0] + " that can " + sp_words[1] + " and also " + sp_words[2]
        return_type = "Allows " + sp_words[0] + " to " + sp_words[1] + " and " + sp_words[2]
    elif pattern == "noun noun verb noun":
        description = "use " + sp_words[0] + " and " + sp_words[1] + " to " + sp_words[2] + " the " + sp_words[3]
        return_type = "Utilizes " + sp_words[0] + " and " + sp_words[1] + " for the action of " + sp_words[2] + "ing " + \
                      sp_words[3]
    else:
        # print("!", api_name, "##", pattern)
        description = "performs operations related to " + " ".join(sp_words)
        return_type = "return the result after " + " ".join(sp_words) + " operation"
        # return pattern, "performs operations related to " + " ".join(sp_words)
    return pattern, description, return_type


def preprocess_api_name(api_name):
    # 移除任何非字母和非下划线字符
    api_name = re.sub(r'[^A-Za-z_]', '', api_name)

    # 检测下划线命名
    if '_' in api_name:
        words = split_snakecase(api_name)
    else:
        words = split_camelcase(api_name)

    # 转换为小写
    words = [word.lower() for word in words]
    words = list(filter(None, words))

    tagged_words = pos_tagging(words)

    pattern, description, return_type = parse_api_name(" ".join(words), tagged_words)

    return pattern, description, return_type

print("API name process init!")
# with open("result/sample_api_msg.pkl", 'rb') as f:
#     sample_api_msg = pickle.load(f)
# # print()
# l = []
# for APIname in sample_api_msg.keys():
#     pattern, description, return_type = preprocess_api_name(APIname)
#     l.append(pattern)
#     print("%%", pattern, "%%", description)  # Output: [('get', 'VB'), ('user', 'NN'), ('name', 'NN')]
#
# # l = list(set(l))
# # print(Counter(l))
# # 筛选出现次数大于等于10次的元素
# filtered_elements = {element: count for element, count in Counter(l).items() if count >= 10}
# # 计算这些元素出现次数之和
# print(len(filtered_elements))
# sum_of_counts = sum(filtered_elements.values())
# print("模式解析占比：", sum_of_counts, "/", len(sample_api_msg.keys()))
