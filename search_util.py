from indic_transliteration import sanscript

class SearchUtil:
    @staticmethod
    def transliterate_query(query, target_script=sanscript.DEVANAGARI):
        """
        Translates english phonetic text to Indic script.
        ITRANS mapping is widely used.
        """
        if not query:
            return ""
        try:
            return sanscript.transliterate(query, sanscript.ITRANS, target_script)
        except Exception as e:
            print(f"Transliteration error: {e}")
            return query

class TrieNode:
    def __init__(self):
        self.word = None
        self.children = {}

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.word = word

    def search(self, word, max_cost=None):
        if max_cost is None:
            # Dynamic scaling
            l = len(word)
            if l <= 4:
                max_cost = 1
            elif l <= 8:
                max_cost = 2
            else:
                max_cost = 3
                
        results = []
        current_row = range(len(word) + 1)
        
        for letter in self.root.children:
            self._levenshtein_trie_search(self.root.children[letter], letter, word, current_row, results, max_cost)
            
        return results

    def _levenshtein_trie_search(self, node, letter, word, prev_row, results, max_cost):
        current_row = [prev_row[0] + 1]

        for i in range(1, len(word) + 1):
            insert_cost = current_row[i - 1] + 1
            delete_cost = prev_row[i] + 1
            replace_cost = prev_row[i - 1] + (word[i - 1] != letter)

            current_row.append(min(insert_cost, delete_cost, replace_cost))

        if current_row[-1] <= max_cost and node.word:
            results.append((node.word, current_row[-1]))

        if min(current_row) <= max_cost:
            for child in node.children:
                self._levenshtein_trie_search(node.children[child], child, word, current_row, results, max_cost)
