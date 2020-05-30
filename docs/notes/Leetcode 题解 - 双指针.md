# 1. 有序数组的两数之和

167\. Two Sum II - Input array is sorted / 两数之和 II - 输入有序数组(Easy)

[Leetcode](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/description/) / [力扣](https://leetcode-cn.com/problems/two-sum-ii-input-array-is-sorted/description/)

```html
Input: numbers={2, 7, 11, 15}, target=9
Output: index1=1, index2=2
```

题目描述：在有序数组中找出两个数，使它们的和为 target。

使用双指针，一个指针指向值较小的元素，一个指针指向值较大的元素。指向较小元素的指针从头向尾遍历，指向较大元素的指针从尾向头遍历。

- 如果两个指针指向元素的和 sum == target，那么得到要求的结果；
- 如果 sum > target，移动较大的元素，使 sum 变小一些；
- 如果 sum < target，移动较小的元素，使 sum 变大一些。

数组中的元素最多遍历一次，时间复杂度为 O(N)。只使用了两个额外变量，空间复杂度为  O(1)。

<div align="center"> <img src="https://cs-notes-1256109796.cos.ap-guangzhou.myqcloud.com/437cb54c-5970-4ba9-b2ef-2541f7d6c81e.gif" width="200px"> </div><br>

```cpp
class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        if(nums.empty()) return {};
        
        int i = 0, j = nums.size() - 1;
        while(nums[i] + nums[j] != target && i < j) {
            if(nums[i] + nums[j] < target) i++;
            else j--;
        }
        return {i + 1, j + 1};
    }
};
```



# 2. 两数平方和

633\. Sum of Square Numbers (Easy)

[Leetcode](https://leetcode.com/problems/sum-of-square-numbers/description/) / [力扣](https://leetcode-cn.com/problems/sum-of-square-numbers/description/)

```html
Input: 5
Output: True
Explanation: 1 * 1 + 2 * 2 = 5
```

题目描述：判断一个非负整数是否为两个整数的平方和。

**题解**：

可以看成是在元素为 0\~target 的有序数组中查找两个数，使得这两个数的平方和为 target，如果能找到，则返回 true，表示 target 是两个整数的平方和。

本题和 167\. Two Sum II - Input array is sorted 类似，只有一个明显区别：一个是和为 target，一个是平方和为 target。本题同样可以使用双指针得到两个数，使其平方和为 target。

本题的关键是右指针的初始化，实现剪枝，从而降低时间复杂度。设右指针为 x，左指针固定为 0，为了使 0<sup>2</sup> + x<sup>2</sup> 的值尽可能接近 target，我们可以将 x 取为 sqrt(target)。

因为最多只需要遍历一次 0\~sqrt(target)，所以时间复杂度为 O(sqrt(target))。又因为只使用了两个额外的变量，因此空间复杂度为 O(1)。

```cpp
class Solution {
public:
    bool judgeSquareSum(int c) {
        if(c < 0) return false;
        long i = 0, j = sqrt(c);
        while(i <= j) {
            long sum = i*i + j*j;
            if(sum == c) return true;
            if(sum > c) j--;
            else i++;
        }
        return false;
    }
};
```

另一种写法：使用for循环控制 i，while循环控制 j

```cpp
class Solution {
public:
    bool judgeSquareSum(int c) {
        if(c < 0) return false;
        for(long i = 0, j = sqrt(c); i <= j; i++) {
            while(j >= 0 && i*i + j*j > c) j--;
            if(i*i + j*j == c) return true;
        }
        return false;
    }
};
```



# 3. 反转字符串中的元音字符✏️

345\. Reverse Vowels of a String (Easy)

[Leetcode](https://leetcode.com/problems/reverse-vowels-of-a-string/description/) / [力扣](https://leetcode-cn.com/problems/reverse-vowels-of-a-string/description/)

```html
Given s = "leetcode", return "leotcede".
```

<div align="center"> <img src="https://cs-notes-1256109796.cos.ap-guangzhou.myqcloud.com/a7cb8423-895d-4975-8ef8-662a0029c772.png" width="400px"> </div><br>

使用双指针，一个指针从头向尾遍历，一个指针从尾到头遍历，当两个指针都遍历到元音字符时，交换这两个元音字符。

为了快速判断一个字符是不是元音字符，我们将全部元音字符添加到集合 HashSet 中，从而以 O(1) 的时间复杂度进行该操作。

- 时间复杂度为 O(N)：只需要遍历所有元素一次
- 空间复杂度 O(1)：只需要使用两个额外变量

<div align="center"> <img src="https://cs-notes-1256109796.cos.ap-guangzhou.myqcloud.com/ef25ff7c-0f63-420d-8b30-eafbeea35d11.gif" width="400px"> </div><br>

```cpp
private final static HashSet<Character> vowels = new HashSet<>(
        Arrays.asList('a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U'));

public String reverseVowels(String s) {
    if (s == null) return null;
    int i = 0, j = s.length() - 1;
    char[] result = new char[s.length()];
    while (i <= j) {
        char ci = s.charAt(i);
        char cj = s.charAt(j);
        if (!vowels.contains(ci)) {
            result[i++] = ci;
        } else if (!vowels.contains(cj)) {
            result[j--] = cj;
        } else {
            result[i++] = cj;
            result[j--] = ci;
        }
    }
    return new String(result);
}
```



# 4. 回文字符串

680\. Valid Palindrome II / 验证回文字符串 II (Easy)

[Leetcode](https://leetcode.com/problems/valid-palindrome-ii/description/) / [力扣](https://leetcode-cn.com/problems/valid-palindrome-ii/description/)

```html
Input: "abca"
Output: True
Explanation: You could delete the character 'c'.
```

题目描述：可以删除一个字符，判断是否能构成回文字符串。

**题解**：

所谓的回文字符串，是指具有左右对称特点的字符串，例如 "abcba" 就是一个回文字符串。

使用双指针可以很容易判断一个字符串是否是回文字符串：令一个指针从左到右遍历，一个指针从右到左遍历，这两个指针同时移动一个位置，每次都判断两个指针指向的字符是否相同，如果都相同，字符串才是具有左右对称性质的回文字符串。

<div align="center"> <img src="https://cs-notes-1256109796.cos.ap-guangzhou.myqcloud.com/fcc941ec-134b-4dcd-bc86-1702fd305300.gif" width="250px"> </div><br>

本题的关键是处理删除一个字符。在使用双指针遍历字符串时，如果出现两个指针指向的字符不相等的情况，我们就试着删除一个字符，再判断删除完之后的字符串是否是回文字符串。

在判断是否为回文字符串时，我们不需要判断整个字符串，因为左指针左边和右指针右边的字符之前已经判断过具有对称性质，所以只需要判断中间的子字符串即可。

在试着删除字符时，我们既可以删除左指针指向的字符，也可以删除右指针指向的字符。

<div align="center"> <img src="https://cs-notes-1256109796.cos.ap-guangzhou.myqcloud.com/db5f30a7-8bfa-4ecc-ab5d-747c77818964.gif" width="300px"> </div><br>

写法1：使用两种模板，for 和 while

```cpp
class Solution {
public:
    bool validPalindrome(string s) {
        for(int i = 0, j = s.size() - 1; i < j; i++, j--) {
            if(s[i] != s[j]) { // 不删元素的话，不是回文，删除元素再判断
                return Palindrome(s, i, j - 1) || Palindrome(s, i + 1, j); // 删除一个字符判断是否是回文
            }
        }
        return true;
    }

    bool Palindrome(string s, int i, int j) {
        while(i < j) {
            if(s[i] != s[j]) return false;
            i++; j--;
        }
        return true;
    }
};
```

写法2：使用一种模板，while

```cpp
class Solution1 {
public:
    bool validPalindrome(string s) {
        int i = 0, j = s.size() - 1;
        while (i < j) {
            if (s[i] != s[j]) return isValid(s, i, j - 1) || isValid(s, i + 1, j);
            ++i; --j;
        }
        return true;
    }
    bool isValid(string s, int i, int j) {
        while (i < j) {
            if (s[i] != s[j]) return false;
            ++i; --j;
        }
        return true;
    }
};
```



# 5. 归并两个有序数组✏️

88\. Merge Sorted Array (Easy)

[Leetcode](https://leetcode.com/problems/merge-sorted-array/description/) / [力扣](https://leetcode-cn.com/problems/merge-sorted-array/description/)

```html
Input:
nums1 = [1,2,3,0,0,0], m = 3
nums2 = [2,5,6],       n = 3

Output: [1,2,2,3,5,6]
```

题目描述：把归并结果存到第一个数组上。

需要从尾开始遍历，否则在 nums1 上归并得到的值会覆盖还未进行归并比较的值。

```cpp
public void merge(int[] nums1, int m, int[] nums2, int n) {
    int index1 = m - 1, index2 = n - 1;
    int indexMerge = m + n - 1;
    while (index1 >= 0 || index2 >= 0) {
        if (index1 < 0) {
            nums1[indexMerge--] = nums2[index2--];
        } else if (index2 < 0) {
            nums1[indexMerge--] = nums1[index1--];
        } else if (nums1[index1] > nums2[index2]) {
            nums1[indexMerge--] = nums1[index1--];
        } else {
            nums1[indexMerge--] = nums2[index2--];
        }
    }
}
```



# 6. 判断链表是否存在环

141\. Linked List Cycle (Easy)

[Leetcode](https://leetcode.com/problems/linked-list-cycle/description/) / [力扣](https://leetcode-cn.com/problems/linked-list-cycle/description/)

使用双指针，一个指针每次移动一个节点，一个指针每次移动两个节点，如果存在环，那么这两个指针一定会相遇。

```cpp
class Solution {
public:
    bool hasCycle(ListNode *head) {
        ListNode *fast = head, *slow = head;
        while(fast && fast->next) {
            fast = fast->next->next;
            slow = slow->next;
            if(fast == slow) return true;
        }
        return false;
    }
};
```



# 7. 最长子序列

524\. Longest Word in Dictionary through Deleting (Medium)

[Leetcode](https://leetcode.com/problems/longest-word-in-dictionary-through-deleting/description/) / [力扣](https://leetcode-cn.com/problems/longest-word-in-dictionary-through-deleting/description/)

```
Input:
s = "abpcplea", d = ["ale","apple","monkey","plea"]

Output:
"apple"
```

题目描述：删除 s 中的一些字符，使得它构成字符串列表 d 中的一个字符串，找出能构成的最长字符串。如果有多个相同长度的结果，返回字典序的最小字符串。

**题解**：

通过删除字符串 s 中的一个字符能得到字符串 t，可以认为 t 是 s 的子序列，我们可以使用双指针来判断一个字符串是否为另一个字符串的子序列。

指针i指向字符串 s，指针 j 指向可能为子序列的字符串 ds，i 指针始终右移一位，当 i，j 指向的字符相等时 j 右移一位。若 ds 为 s 的子序列，则 j 最终指向 '\0' 位置，否则指向ds中某个字符。

```cpp
class Solution {
public:
    string findLongestWord(string s, vector<string>& d) {
        string res = "";
        for(auto ds : d) {
            if(isSubStr(s, ds)) {
                // 选长度大的，若长度相等，选字典序小的
                if(ds.size() > res.size() || (ds.size() == res.size() && ds < res))
                    res = ds;
            }
        }
        return res;
    }

    bool isSubStr(string s, string ds) {
        int i = 0, j = 0;
        while(i < s.size() && j < ds.size()) {
            if(s[i] == ds[j]) j++;
            i++;
        }
        return j == ds.size();
    }
};
```



# 8. 无重复最长子串

[Leetcode 3. 无重复字符的最长子串](https://leetcode-cn.com/problems/longest-substring-without-repeating-characters/)

题目描述：给定一个字符串，请你找出其中不含有重复字符的 **最长子串** 的长度。

```
输入: "abcabcbb"
输出: 3 
```

**题解**：

使用双指针，或称之为滑动窗口。i 指针每次右移一位，当 i 指针指向的字符在区间中出现两次时，j 指针右移直到 i 指针指向的字符在区间中仅出现一次。

方法1：字符的种类有限，可使用数组模拟哈希表，存储字符出现的次数，速度很快。

- 写法1：每次直接插入，即在判断之前插入，因而需判断某字符是否出现了两次。
- 写法2：在while循环后插入，即在判断之后插入，那么只需判断某字符是否已出现过一次。

```cpp
class Solution {
public:
    int lengthOfLongestSubstring(string s) {
        int n = s.size();

        int cnt[256] = {0}; // 注意初始化
        int res = 0;
        for(int i = 0, j = 0; i < n; i++) { // 扩大区间
            cnt[s[i]]++; // 扩大区间，出现次数加1
            while(cnt[s[i]] > 1) { // 出现两次
                cnt[s[j]]--; // 缩小区间，出现次数减1
                j++; // 缩小区间
            }
            res = max(res, i - j + 1);
        }
        return res;
    }
};

// 写法2
class Solution {
public:
    int lengthOfLongestSubstring(string s) {
        int n = s.size();

        int cnt[256] = {0};
        int res = 0;
        for(int i = 0, j = 0; i < n; i++) {
            while(cnt[s[i]] > 0) {
                cnt[s[j]]--;
                j++;
            }
            cnt[s[i]]++;
            res = max(res, i - j + 1);
        }
        return res;
    }
};
```

方法2：使用哈希表unordered_map存储出现的字符，速度较慢。注意unordered_map不能存储重复的数据，即仅能判断一个字符当前出现的次数是否为0或1，因而需将插入代码放到while循环之后，如果出现了重复的字符，那么下次判断时，此字符出现的次数为1。

```cpp
class Solution1 {
public:
    int lengthOfLongestSubstring(string s) {
        int n = s.size();

        unordered_set<char> us;
        int res = 0;
        for(int i = 0, j = 0; i < n; i++) {
            while(us.count(s[i]) > 0) {
                us.erase(s[j]);
                j++;
            }
            us.insert(s[i]);

            res = max(res, i - j + 1);
        }

        return res;
    }
};
```

方法3：若想保存每个字符出现的次数，可以使用unordered_map，不推荐

```cpp
class Solution {
public:
    int lengthOfLongestSubstring(string s) {
        int n = s.size();

        unordered_map<char, int> umap;
        int res = 0;
        for(int i = 0, j = 0; i < n; i++) {
            umap[s[i]]++;
            while(umap[s[i]] > 1) {
                umap[s[j]]--;
                j++;
            }
            res = max(res, i - j + 1);
        }

        return res;
    }
};
```



# 9. 移动零

[Leetcode 283. 移动零 (Easy)](https://leetcode-cn.com/problems/move-zeroes/)

```
Input: [0,1,0,3,12]
Output: [1,3,12,0,0]
```

**题解**：

使用快慢指针，快指针遍历数组每个元素，遇到非0元素则与慢指针交换，并且慢指针后移一位，这样做的结果是：慢指针之前的所有元素都是非零的，慢指针始终指向0

```cpp
class Solution {
public:
    void moveZeroes(vector<int>& nums) {
        for(int i = 0, j = 0; i < nums.size(); i++) { // i为快指针，j为慢指针
            if(nums[i] != 0) swap(nums[i], nums[j++]);
        }
    }
};
```

