## architecture

# ![alt text](architecture.png)

## the output from llmm

{
"title": "Robot Grid Pathfinding",
"description": "Find a path for a robot to reach the bottom-right corner of a grid from the top-left corner while avoiding obstacles.",
"difficulty": "medium",
"imageUrl": "/static/generated_images/image_ce4903b392.png",
"visual": {
"hasVisual": true,
"type": "illustration",
"url": "/static/generated_images/image_ce4903b392.png",
"diagramCode": null
},
"testCases": [
{
"input": "{\"grid\": [[0, 0, 1], [0, 0, 0], [1, 0, 0]]}",
"output": "[[0, 0], [0, 1], [1, 1], [1, 2], [2, 2]]"
},
{
"input": "{\"grid\": [[0, 1, 0], [0, 0, 0], [0, 1, 0]]}",
"output": "[[0, 0], [1, 0], [1, 1], [1, 2], [2, 2]]"
},
{
"input": "{\"grid\": [[0, 0, 0], [0, 1, 0], [0, 0, 0]]}",
"output": "[[0, 0], [0, 1], [0, 2], [1, 2], [2, 2]]"
},
{
"input": "{\"grid\": [[0, 0, 0], [0, 0, 0], [0, 0, 0]]}",
"output": "[[0, 0], [0, 1], [0, 2], [1, 2], [2, 2]]"
},
{
"input": "{\"grid\": [[1, 1, 1], [1, 1, 1], [1, 1, 1]]}",
"output": "null"
}
],
"codeSnippets": [
{
"language": "python",
"startSnippet": "def solve(self, grid):",
"midSnippet": "",
"endSnippet": "return path"
},
{
"language": "java",
"startSnippet": "public int[][] solve(int[][] grid) {",
"midSnippet": "",
"endSnippet": "}"
},
{
"language": "cpp",
"startSnippet": "vector<vector<int>> solve(vector<vector<int>>& grid) {",
"midSnippet": "",
"endSnippet": "}"
}
],
"editorial": "### Optimal Solution Walkthrough\n\n`python\nimport sys, json\nfrom collections import deque\n\nclass Solution:\n    def solve(self, grid):\n        m, n = len(grid), len(grid[0])\n        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]\n        queue = deque([(0, 0, [])])\n        visited = set((0, 0))\n        while queue:\n            x, y, path = queue.popleft()\n            path = path + [(x, y)]\n            if x == m - 1 and y == n - 1:\n                return path\n            for dx, dy in directions:\n                nx, ny = x + dx, y + dy\n                if (0 <= nx < m and 0 <= ny < n and grid[nx][ny] == 0 and (nx, ny) not in visited):\n                    queue.append((nx, ny, path))\n                    visited.add((nx, ny))\n        return None\n\n    def build_input(self, raw):\n        return raw['grid']\n\n    def serialize_output(self, result):\n        return result\n\nif __name__ == '__main__':\n    import sys, json\n    raw = json.loads(sys.stdin.read())\n    solution = Solution()\n    grid = solution.build_input(raw)\n    result = solution.solve(grid)\n    output = solution.serialize_output(result)\n    print(json.dumps(output))\n`",
"topic": "Pathfinding",
"\_cache_hit": false
}

as well as

{
"title": "Invert Binary Tree",
"description": "Write a function that inverts a binary tree. For example, the following tree: 4 / \\ 2 7 / \\ / \\ 1 3 6 9 should become: 4 / \\ 7 2 / \\ / \\ 9 6 3 1",
"difficulty": "medium",
"imageUrl": "https://mermaid.ink/svg/Z3JhcGggVEQKICAgIEEoKDQpKQogICAgQSAtLT4gQigoMikpCiAgICBBIC0tPiBDKCg3KSkKICAgIEIgLS0+IEQoKDEpKQogICAgQiAtLT4gRSgoMykpCiAgICBDIC0tPiBGKCg2KSkKICAgIEMgLS0+IEcoKDkpKQ==",
"visual": {
"hasVisual": true,
"type": "tree",
"url": "https://mermaid.ink/svg/Z3JhcGggVEQKICAgIEEoKDQpKQogICAgQSAtLT4gQigoMikpCiAgICBBIC0tPiBDKCg3KSkKICAgIEIgLS0+IEQoKDEpKQogICAgQiAtLT4gRSgoMykpCiAgICBDIC0tPiBGKCg2KSkKICAgIEMgLS0+IEcoKDkpKQ==",
"diagramCode": "graph TD\n A((4))\n A --> B((2))\n A --> C((7))\n B --> D((1))\n B --> E((3))\n C --> F((6))\n C --> G((9))"
},
"testCases": [
{
"input": "{\"val\": 4, \"left\": {\"val\": 2, \"left\": {\"val\": 1, \"left\": null, \"right\": null}, \"right\": {\"val\": 3, \"left\": null, \"right\": null}}, \"right\": {\"val\": 7, \"left\": {\"val\": 6, \"left\": null, \"right\": null}, \"right\": {\"val\": 9, \"left\": null, \"right\": null}}}",
"output": "{\"val\": 4, \"left\": {\"val\": 7, \"left\": {\"val\": 9, \"left\": null, \"right\": null}, \"right\": {\"val\": 6, \"left\": null, \"right\": null}}, \"right\": {\"val\": 2, \"left\": {\"val\": 3, \"left\": null, \"right\": null}, \"right\": {\"val\": 1, \"left\": null, \"right\": null}}}"
}
],
"codeSnippets": [
{
"language": "python",
"startSnippet": "class TreeNode:\n def __init__(self, x):\n self.val = x\n self.left = None\n self.right = None\n\nclass Solution:\n def invertTree(self, root):\n",
"midSnippet": "",
"endSnippet": " return root"
},
{
"language": "java",
"startSnippet": "public class TreeNode {\n int val;\n TreeNode left;\n TreeNode right;\n TreeNode(int x) { val = x; }\n}\n\nclass Solution {\n public TreeNode invertTree(TreeNode root) {",
"midSnippet": "",
"endSnippet": " }"
},
{
"language": "cpp",
"startSnippet": "struct TreeNode {\n int val;\n TreeNode *left;\n TreeNode *right;\n TreeNode(int x) : val(x), left(NULL), right(NULL) {}\n};\n\nclass Solution {\npublic:\n TreeNode* invertTree(TreeNode* root) {",
"midSnippet": "",
"endSnippet": " }"
}
],
"editorial": "### Optimal Solution Walkthrough\n\n`python\nimport json\n\nclass TreeNode:\n    def __init__(self, x):\n        self.val = x\n        self.left = None\n        self.right = None\n\nclass Solution:\n    def invertTree(self, root):\n        if root is None:\n            return None\n        root.left, root.right = self.invertTree(root.right), self.invertTree(root.left)\n        return root\n\n    @staticmethod\n    def build_input(raw):\n        if raw is None:\n            return None\n        root = TreeNode(raw['val'])\n        root.left = Solution.build_input(raw.get('left'))\n        root.right = Solution.build_input(raw.get('right'))\n        return root\n\n    @staticmethod\n    def serialize_output(root):\n        if root is None:\n            return None\n        return {\n            'val': root.val,\n            'left': Solution.serialize_output(root.left),\n            'right': Solution.serialize_output(root.right)\n        }\n\nif __name__ == '__main__':\n    import sys\n    raw = json.loads(sys.stdin.read())\n    root = Solution.build_input(raw)\n    solution = Solution()\n    inverted_root = solution.invertTree(root)\n    output = Solution.serialize_output(inverted_root)\n    print(json.dumps(output))\n`",
"topic": "binary_tree",
"\_cache_hit": false
}
