
链表是空节点，或者有一个值和一个指向下一个链表的指针，因此很多链表问题可以用递归来处理。



#  1. 找出两个链表的交点

160\. Intersection of Two Linked Lists / 相交链表 (Easy)

[Leetcode](https://leetcode.com/problems/intersection-of-two-linked-lists/description/) / [力扣](https://leetcode-cn.com/problems/intersection-of-two-linked-lists/description/)

例如以下示例中 A 和 B 两个链表相交于 c1：

```html
A:          a1 → a2
                    ↘
                      c1 → c2 → c3
                    ↗
B:    b1 → b2 → b3
```

但是不会出现以下相交的情况，因为每个节点只有一个 next 指针，也就只能有一个后继节点，而以下示例中节点 c 有两个后继节点。

```html
A:          a1 → a2       d1 → d2
                    ↘  ↗
                      c
                    ↗  ↘
B:    b1 → b2 → b3        e1 → e2
```



要求时间复杂度为 O(N)，空间复杂度为 O(1)。如果不存在交点则返回 null。

设 A 的长度为 a + c，B 的长度为 b + c，其中 c 为尾部公共部分长度，可知 a + c + b = b + c + a。

当访问 A 链表的指针访问到链表尾部时，令它从链表 B 的头部开始访问链表 B；同样地，当访问 B 链表的指针访问到链表尾部时，令它从链表 A 的头部开始访问链表 A。这样就能控制访问 A 和 B 两个链表的指针能同时访问到交点。

如果不存在交点，那么 a + b = b + a，以下实现代码中 l1 和 l2 会同时为 null，从而退出循环。

```cpp
class Solution {
public:
    ListNode *getIntersectionNode(ListNode *headA, ListNode *headB) {
        ListNode *p1 = headA, *p2 = headB;
        while(p1 != p2) {
            p1 = !p1 ? headB : p1->next;
            p2 = !p2 ? headA : p2->next;
        }
        return p1;
    }
};
```

如果只是判断是否存在交点，那么就是另一个问题，即 [编程之美 3.6]() 的问题。有两种解法：

- 把第一个链表的结尾连接到第二个链表的开头，看第二个链表是否存在环；
- 或者直接比较两个链表的最后一个节点是否相同。



#  2. 链表反转

206\. Reverse Linked List / 反转链表 (Easy)

[Leetcode](https://leetcode.com/problems/reverse-linked-list/description/) / [力扣](https://leetcode-cn.com/problems/reverse-linked-list/description/)

**题解**：

方法1：指针操作

```cpp
class Solution {
public:
    ListNode* reverseList(ListNode* head) {
        ListNode *pre = NULL, *next = NULL;

        while(head) {
            next = head->next;
            head->next = pre;
            pre = head;
            head = next;
        }
        return pre;
    }
};
```

方法2：递归

```cpp
class Solution {
public:
    ListNode* reverseList(ListNode* head) {
        if(!head || !head->next) return head;

        ListNode *next = head->next;
        ListNode *newhead = reverseList(next);
        next->next = head;
        head->next = NULL;
        return newhead;
    }
};
```

方法3：头插法

```cpp
class Solution {
public:
    ListNode* reverseList(ListNode* head) {
        ListNode *newhead = new ListNode(-1);

        while(head) {
            ListNode *next = head->next;
            head->next = newhead->next;
            newhead->next = head;
            head = next;
        }
        return newhead->next;
    }
};
```



#  3. 合并两个有序链表

21\. Merge Two Sorted Lists / 合并两个有序链表 (Easy)

[Leetcode](https://leetcode.com/problems/merge-two-sorted-lists/description/) / [力扣](https://leetcode-cn.com/problems/merge-two-sorted-lists/description/)

**题解**：

递归：

```cpp
class Solution {
public:
    ListNode* mergeTwoLists(ListNode* l1, ListNode* l2) {
        if(!l1) return l2;
        if(!l2) return l1;
        if(l1->val <= l2->val) {
            l1->next = mergeTwoLists(l1->next, l2);
            return l1;
        } else {
            l2->next = mergeTwoLists(l1, l2->next);
            return l2;
        }
    }
};
```

迭代：

```cpp
class Solution {
public:
    ListNode* mergeTwoLists(ListNode* l1, ListNode* l2) {
        ListNode* head = new ListNode(-1);
        ListNode* cur = head;
        while(l1 && l2) {
            if(l1->val <= l2->val) {
                cur->next = l1;
                l1 = l1->next;
            } else {
                cur->next = l2;
                l2 = l2->next;
            }
            cur = cur->next;
        }

        cur->next = l1 ? l1 : l2; // 处理未遍历完的节点
        return head->next;
    }
};
```



#  4. 删除链表中的节点

[Leetcode 237. 删除链表中的节点](https://leetcode-cn.com/problems/delete-node-in-a-linked-list/)

删除链表中的某个节点，此节点不会是尾节点

**题解**：

从链表里删除一个节点 node 的最常见方法是修改之前节点的 next 指针，使其指向之后的节点。

<img src="https://pic.leetcode-cn.com/3579a496897df5321c110bf1301872b6e10c342f5e400ce45d2db0348d00d715-file_1555866623326" alt="img" style="zoom:67%;" />

因为，我们无法访问我们想要删除的节点 之前 的节点，我们始终不能修改该节点的 next 指针。相反，我们必须将想要删除的节点的值替换为它后面节点中的值，然后删除它之后的节点。

<img src="https://pic.leetcode-cn.com/858fae01d89c2080eb7e45a1f9d9a2b2f76e1a5c87815b324fd946e0bd8da495-file_1555866651920" alt="img" style="zoom:67%;" />



<img src="https://pic.leetcode-cn.com/902dc5d3f8c44d3cbc0b6e837711cad2eefc021fd2b9de8dfabc6d478bc779b1-file_1555866680932" alt="img" style="zoom:67%;" />

因为我们知道要删除的节点不是列表的末尾，所以我们可以保证这种方法是可行的

```cpp
class Solution {
public:
    void deleteNode(ListNode* node) {
        node->val = node->next->val;
        node->next = node->next->next;
    }
};
```



#  5. 删除链表的倒数第 n 个节点

19\. Remove Nth Node From End of List /  删除链表的倒数第N个节点 (Medium)

[Leetcode](https://leetcode.com/problems/remove-nth-node-from-end-of-list/description/) / [力扣](https://leetcode-cn.com/problems/remove-nth-node-from-end-of-list/description/)

```html
Given linked list: 1->2->3->4->5, and n = 2.
After removing the second node from the end, the linked list becomes 1->2->3->5.
```

**题解**：首先快指针先向前走N步，如果此时快指针指向空，说明N为链表的长度，则需要移除的为首元素，那么此时返回 head->next 即可；如果快指针未指向空，再继续往下走，此时慢指针也跟着走，直到快指针指向最后一个元素时停止，此时慢指针指向要移除元素的**前一个元素**，再修改指针跳过需要移除的元素即可

```cpp
class Solution {
public:
    ListNode* removeNthFromEnd(ListNode* head, int n) {
        auto fast = head, slow = head;

        for(int i = 0; i < n; i++) fast = fast->next; // 快指针先走k步
        if(!fast) return head->next; // 若快指针走到空节点，则要删除的是头结点

        while(fast->next) { // 快慢指针同时右移，直到快指针指向最后一个节点
            fast = fast->next;
            slow = slow->next;
        }
        // 此时慢指针指向倒数第k个节点的前一个节点， 慢指针指向下下个节点即可
        slow->next = slow->next->next;
        return head;
    }
};
```



#  6. 删除有序链表中的重复节点

83\. Remove Duplicates from Sorted List / 删除排序链表中的重复元素 (Easy)

[Leetcode](https://leetcode.com/problems/remove-duplicates-from-sorted-list/description/) / [力扣](https://leetcode-cn.com/problems/remove-duplicates-from-sorted-list/description/)

```html
Given 1->1->2, return 1->2.
Given 1->1->2->3->3, return 1->2->3.
```

**题解**：

方法1：迭代

遍历链表，每个结点和其后面的结点比较，如果结点值相同了，只要将前面结点的 next 指针跳过紧挨着的相同值的结点，指向后面一个结点。这样遍历下来，所有重复的结点都会被跳过，留下的链表就是没有重复项的了。

```cpp
class Solution1 {
public:
    ListNode* deleteDuplicates(ListNode* head) {
        auto curr = head; // 因为要返回原来的头节点，这里新建指针进行遍历
        while(curr && curr->next) { // 这里判断当前节点和下一节点是否为空，因为需要用到下下个节点
            if(curr->val == curr->next->val) {
                curr->next = curr->next->next;
            } else curr = curr->next;
        }
        return head;
    }
};
```



方法2：递归

首先判断是否至少有两个结点，若不是的话，直接返回 head。否则对 head->next 调用递归函数，并赋值给 head->next。这里可能比较晕，先看后面一句，返回的时候，head 结点先跟其身后的结点进行比较，如果值相同，那么返回后面的一个结点，当前的 head 结点就被跳过了，而如果不同的话，还是返回 head 结点。可以发现了，进行实质上的删除操作是在最后一句进行了，再来看第二句，对 head 后面的结点调用递归函数，那么就应该 suppose 返回来的链表就已经没有重复项了，此时接到 head 结点后面，在第三句的时候再来检查一下 head 是否又 duplicate 了，实际上递归一直走到了末尾结点，再不断的回溯回来，进行删除重复结点

```cpp
class Solution {
public:
    ListNode* deleteDuplicates(ListNode* head) {
        if(!head || !head->next) return head;
        head->next = deleteDuplicates(head->next);
        return head->val == head->next->val ? head->next : head;
    }
};
```



#  7. 交换链表中的相邻结点

24\. Swap Nodes in Pairs / 两两交换链表中的节点 (Medium)

[Leetcode](https://leetcode.com/problems/swap-nodes-in-pairs/description/) / [力扣](https://leetcode-cn.com/problems/swap-nodes-in-pairs/description/)

```html
Given 1->2->3->4, you should return the list as 2->1->4->3.
```

题目要求：不能修改结点的 val 值，O(1) 空间复杂度。

**题解**：

方法1：迭代

<img src="https://gitee.com//MrRen-sdhm/Images/raw/master/img/20200513141450.png" alt="128ad64e800b77294cb3b31ed6b97e3b60a786207a1216fee2e41781fa950b42-frame_00003" style="zoom:67%;" />

交换两个节点实际上和四个节点有关系，需要修改3次指针的指向，为了交换头结点与其下一个节点，需要在头结点之前创建虚拟节点。

- 设置指针指向当前节点的下下个节点，即第二个要交换的节点，因为后面要断开指向第二个要交换节点的指针，不保存的话，之后就无法访问第二个要交换的节点了
- 先将第一个节点的下一个节点指向第二个节点的后一个节点
- 再将第二个节点的下一个节点指向第一个节点
- 然后将当前节点的下一个节点指向第二个节点
- 最后更新当前节点为第二个节点的下一个节点，即原来的第一个节点

```cpp
class Solution {
public:
    ListNode* swapPairs(ListNode* head) {
        ListNode *dummy = new ListNode(-1), *pre = dummy;
        dummy->next = head;
        while(pre->next && pre->next->next) { // 交换的是next和next->next，确保同时存在
            ListNode *t = pre->next->next; // t指针指向要交换的第二个节点
            
            pre->next->next = t->next; // 第一个节点的下一个节点改为第二个节点的下一个节点
            t->next = pre->next; // 第二个节点的下一个节点改为第一个节点
            pre->next = t; // 当前节点的下一个节点改为原第二个节点
            
            pre = t->next; // 当前节点改为第二个节点的下一个节点，即原来的第一个节点
        }
        return dummy->next;
    }
};
```



方法2：递归

利用回溯的思想，递归遍历到链表末尾，然后先交换末尾两个，然后依次往前交换

```cpp
class Solution {
public:
    ListNode* swapPairs(ListNode* head) {
        if (!head || !head->next) return head;
        ListNode *t = head->next;
        head->next = swapPairs(head->next->next);
        t->next = head;
        return t;
    }
};
```



#  8. 链表求和

2\. Add Two Numbers / 两数相加 (Medium)

[Leetcode](https://leetcode.com/problems/add-two-numbers/) / [力扣](https://leetcode-cn.com/problems/add-two-numbers/)

```
Input: (2 -> 4 -> 3) + (5 -> 6 -> 4)
Output: 7 -> 0 -> 8
Explanation: 342 + 465 = 807.
```

**题解**：

为了避免两个输入链表同时为空，我们建立一个 dummy 结点，将两个结点相加生成的新结点按顺序加到 dummy 结点之后，由于 dummy 结点本身不能变，所以用一个指针 cur 来指向新链表的最后一个结点。好，可以开始让两个链表相加了，这道题好就好在最低位在链表的开头，所以可以在遍历链表的同时按从低到高的顺序直接相加

- while 循环的条件两个链表中只要有一个不为空，由于链表可能为空，所以在取当前结点值的时候，先判断一下，若为空则取0，否则取结点值

- 然后把两个结点值相加，同时还要加上进位 carry。然后更新 carry，直接 sum/10 即可，然后以 sum%10 为值建立一个新结点，连到 cur 后面，然后 cur 移动到下一个结点

- 之后再更新两个结点，若存在，则指向下一个位置

- while 循环退出之后，最高位的进位问题要最后特殊处理一下，若 carry 为1，则再建一个值为1的结点

  - ```
    链表1：4->NULL
    链表2：6->NULL
    未处理的结果：0->NULL
    4+6=10，处理最后一位时carry=1，因而需要单独创建一个值为1的节点
    处理后的结果：0->1
    ```

    

```cpp
class Solution {
public:
    ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {
        ListNode *dummy = new ListNode(-1), *cur = dummy;
        int carry = 0; // 进位
        while(l1 || l2) {
            int val1 = l1 ? l1->val : 0; // 为空时值记为0
            int val2 = l2 ? l2->val : 0; // 为空时值记为0
            int sum = val1 + val2 + carry; // 节点值加上次的进位
            carry = sum / 10; // 计算进位

            cur->next = new ListNode(sum % 10); // 创建新节点，节点值模10

            if(l1) l1 = l1->next; // l1非空则右移
            if(l2) l2 = l2->next; // l2非空则右移
            cur = cur->next; // 结果链表指针右移
        }
        if(carry) cur->next = new ListNode(1); // 若最高位需要进位，则创建值为1的新节点
        return dummy->next;
    }
};
```



------



445\. Add Two Numbers II / 两数相加 II (Medium)

[Leetcode](https://leetcode.com/problems/add-two-numbers-ii/description/) / [力扣](https://leetcode-cn.com/problems/add-two-numbers-ii/description/)

```html
Input: (7 -> 2 -> 4 -> 3) + (5 -> 6 -> 4)
Output: 7 -> 8 -> 0 -> 7
```

题目要求：不能修改原始链表。

**题解**：这道题的最高位在链表首位置，如果给链表翻转一下的话就跟上一道题目一样了，这题要求不能修改原始来链表。由于加法需要从最低位开始运算，而最低位在链表末尾，链表只能从前往后遍历，没法取到前面的元素，那怎么办呢？可以利用栈来保存所有的元素，然后利用栈的后进先出的特点就可以从后往前取数字了。

- 首先遍历两个链表，将所有数字分别压入两个栈s1和s2中

- 建立一个虚拟头结点，然后开始循环，如果栈不为空，则将栈顶数字加入sum中，然后新建一个进位节点node，因为先计算的为低位，后计算的为高位，通过头插法逆序将新节点插入到结果链表中即可获得高位->低位的顺序
- 若最后一位需要进位，则需再创建一个值为1的节点

写法1：

```cpp
class Solution {
public:
    ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {
        stack<int> stk1, stk2;
        ListNode *p1 = l1, *p2 = l2;
        while(p1) { stk1.push(p1->val); p1 = p1->next; } // 链表1节点值入栈
        while(p2) { stk2.push(p2->val); p2 = p2->next; } // 链表2节点值入栈

        ListNode *dummy = new ListNode(-1);
        int carry = 0;
        while(!stk1.empty() || !stk2.empty()) { // 有一个栈非空，取值
            int val1 = stk1.empty() ? 0 : stk1.top();
            int val2 = stk2.empty() ? 0 : stk2.top();
            int sum = val1 + val2 + carry;
            carry = sum / 10;

            // 头插法将新节点插入头结点之后
            ListNode *node = new ListNode(sum % 10); // 新建节点
            node->next = dummy->next;
            dummy->next = node;

            if(!stk1.empty()) stk1.pop(); // 弹出使用过的节点值
            if(!stk2.empty()) stk2.pop();
        }

        if(carry) { // 处理最后一位需要进位
            ListNode *node = new ListNode(1);
            node->next = dummy->next;
            dummy->next = node;
        }
        return dummy->next;
    }
};
```



写法2：处理最后一位的代码也可放到while循环中，若 carry != 0 说明需要处理最后一位的进位问题，符合while循环的处理逻辑，可放入while循环中处理。

```cpp
class Solution {
public:
    ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {
        stack<int> stk1, stk2;
        ListNode *p1 = l1, *p2 = l2;
        while(p1) { stk1.push(p1->val); p1 = p1->next; } // 链表1节点值入栈
        while(p2) { stk2.push(p2->val); p2 = p2->next; } // 链表2节点值入栈

        ListNode *dummy = new ListNode(-1);
        int carry = 0;
        while(!stk1.empty() || !stk2.empty() || carry != 0) { // 处理最后一次进位
            int val1 = stk1.empty() ? 0 : stk1.top();
            int val2 = stk2.empty() ? 0 : stk2.top();
            int sum = val1 + val2 + carry;
            carry = sum / 10;

            // 头插法将新节点插入头结点之后
            ListNode *node = new ListNode(sum % 10); // 新建节点
            node->next = dummy->next;
            dummy->next = node;

            if(!stk1.empty()) stk1.pop(); // 弹出使用过的节点值
            if(!stk2.empty()) stk2.pop();
        }
        return dummy->next;
    }
};
```



#  9. 回文链表

234\. Palindrome Linked List (Easy)

[Leetcode](https://leetcode.com/problems/palindrome-linked-list/description/) / [力扣](https://leetcode-cn.com/problems/palindrome-linked-list/description/)

题目要求：以 O(1) 的空间复杂度来求解。

切成两半，把后半段反转，然后比较两半是否相等。

```cpp
public boolean isPalindrome(ListNode head) {
    if (head == null || head.next == null) return true;
    ListNode slow = head, fast = head.next;
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
    }
    if (fast != null) slow = slow.next;  // 偶数节点，让 slow 指向下一个节点
    cut(head, slow);                     // 切成两个链表
    return isEqual(head, reverse(slow));
}

private void cut(ListNode head, ListNode cutNode) {
    while (head.next != cutNode) {
        head = head.next;
    }
    head.next = null;
}

private ListNode reverse(ListNode head) {
    ListNode newHead = null;
    while (head != null) {
        ListNode nextNode = head.next;
        head.next = newHead;
        newHead = head;
        head = nextNode;
    }
    return newHead;
}

private boolean isEqual(ListNode l1, ListNode l2) {
    while (l1 != null && l2 != null) {
        if (l1.val != l2.val) return false;
        l1 = l1.next;
        l2 = l2.next;
    }
    return true;
}
```



#  10. 分隔链表

725\. Split Linked List in Parts(Medium)

[Leetcode](https://leetcode.com/problems/split-linked-list-in-parts/description/) / [力扣](https://leetcode-cn.com/problems/split-linked-list-in-parts/description/)

```html
Input:
root = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], k = 3
Output: [[1, 2, 3, 4], [5, 6, 7], [8, 9, 10]]
Explanation:
The input has been split into consecutive parts with size difference at most 1, and earlier parts are a larger size than the later parts.
```

题目描述：把链表分隔成 k 部分，每部分的长度都应该尽可能相同，排在前面的长度应该大于等于后面的。

```cpp
public ListNode[] splitListToParts(ListNode root, int k) {
    int N = 0;
    ListNode cur = root;
    while (cur != null) {
        N++;
        cur = cur.next;
    }
    int mod = N % k;
    int size = N / k;
    ListNode[] ret = new ListNode[k];
    cur = root;
    for (int i = 0; cur != null && i < k; i++) {
        ret[i] = cur;
        int curSize = size + (mod-- > 0 ? 1 : 0);
        for (int j = 0; j < curSize - 1; j++) {
            cur = cur.next;
        }
        ListNode next = cur.next;
        cur.next = null;
        cur = next;
    }
    return ret;
}
```



#  11. 链表元素按奇偶聚集

328\. Odd Even Linked List (Medium)

[Leetcode](https://leetcode.com/problems/odd-even-linked-list/description/) / [力扣](https://leetcode-cn.com/problems/odd-even-linked-list/description/)

```html
Example:
Given 1->2->3->4->5->NULL,
return 1->3->5->2->4->NULL.
```

```cpp
public ListNode oddEvenList(ListNode head) {
    if (head == null) {
        return head;
    }
    ListNode odd = head, even = head.next, evenHead = even;
    while (even != null && even.next != null) {
        odd.next = odd.next.next;
        odd = odd.next;
        even.next = even.next.next;
        even = even.next;
    }
    odd.next = evenHead;
    return head;
}
```



# 12. 排序链表

[Leetcode 148. 排序链表](https://leetcode-cn.com/problems/sort-list/)  / [AcWing 1451. 单链表快速排序](https://www.acwing.com/problem/content/1453/)

**题解**：

方法1：快速排序，稳定，不修改val值，仅修改指针指向，时间复杂度O(nlogn)，空间复杂度O(logn)。[视频讲解](https://www.bilibili.com/video/BV15E41137GE?t=2323)

为了像数组快排一样划分区间，可以创建3个链表，分别存放小于、等于、大于枢轴节点值的节点。及创建3个头结点left、right、mid，然后遍历链表，将小于枢轴的的节点连到left的末尾，等于的连到mid末尾，大于的连到right末尾。然后递归地排left和right链表，最后将三个链表按left-mid-right的顺序连接起来即可。这里**定义三个链表，然后通过指针操作来排序**，是与数组快排的一个最大的不同点。

注意：

- 需要定义三个虚拟头结点，但实际使用时需通过**->next获取真实节点**
- 需要定义三个指针，指向各链表的非空尾节点，并在插入节点后**更新**
- 在分配好各节点的位置后，需要将尾节点的下一节点**置为空**，表示链表结束
- 在递归排序左右链表后进行链表的拼接，中间链表无需排序
- **中间链表不一定存在**，因而在第一次拼接后，仍需从左侧链表的头结点开始寻找当前链表的尾节点

```cpp
class Solution {
public:
    ListNode* sortList(ListNode* head) {
        if(!head || !head->next) return head; // 没有节点或只有一个节点

        // 创建三个虚拟头结点
        auto left = new ListNode(-1), mid = new ListNode(-1), right = new ListNode(-1);
        auto ltail = left, mtail = mid, rtail = right; // 每次在链尾插入，创建指向链尾的指针
        int val = head->val; // 第一个节点作为枢轴

        // 根据枢轴大小将各节点连接到对应的链表
        for(auto p = head; p; p = p->next) {
            if(p->val < val) ltail = ltail->next = p; // 当前节点小于枢轴，放到left链表尾部，并记录新的尾节点
            else if(p->val == val) mtail = mtail->next = p;
            else rtail = rtail->next = p;
        }
        ltail->next = mtail->next = rtail->next = NULL; // 链尾指向空

        // 递归排序左右链表，注意要操作的是真实的头结点left/right->next
        left->next = sortList(left->next); // 排序后的真实头结点替换原来的真实头结点
        right->next = sortList(right->next);

        // 拼接三个链表
        get_tail(left)->next = mid->next; // 左侧链表的尾部连接到中间链表的开头
        get_tail(left)->next = right->next; // 中间链表不一定存在，还是从左侧链表的头部开始找当前链表的尾部

        return left->next; // 返回连接后的真实头结点
    }

    ListNode* get_tail(ListNode * head) {
        while(head->next) head = head->next;
        return head;
    }
};
```

面试时为了更加严谨，最好释放申请的空间

```cpp
        // 释放空间
        auto p = left->next;
        delete left, delete right, delete mid; // 释放申请的空间
        return p; // 返回连接后的真实头结点
	}
```



方法2：自顶向下归并排序-递归，稳定，时间复杂度O(nlogn)，空间复杂度O(logn)

归并排序的核心是一个 merge() 函数，其主要是合并两个有序链表。由于两个链表是要有序的才能比较容易 merge，那么对于一个无序的链表，如何才能拆分成有序的两个链表呢？什么时候两个链表一定都是有序的？就是当两个链表各只有一个结点的时候，一定是有序的。而归并排序的核心其实是分治法，就是将链表从中间断开，分成两部分，左右两边再分别调用排序的递归函数 sortList()，得到各自有序的链表后，再进行 merge()，这样整体就是有序的了。因为子链表的递归函数中还是会再次拆成两半，当拆到链表只有一个结点时，无法继续拆分了，而这正好满足了前面所说的“一个结点的时候一定是有序的”，这样就可以进行 merge 了。然后再回溯回去，每次得到的都是有序的链表，然后进行 merge，直到还原整个长度。

两个主要步骤：

- 寻找中点：
  - 快慢指针，快指针走两步，慢指针走一步，那么在遍历完链表的时候，慢指针指向的位置就是中点。
  - 需要注意的是，由于链表是通过遍历来确定长度的，所以再确认完中点之后，需要切开链表，所以此时还需要用一个变量来保存中点节点的前驱，用以切断链表。
  - <img src="https://pic.leetcode-cn.com/afcf1747cb95435f482d9a2e27fcb7e6528554b0d56e93b044a39680e7a93f3f-image.png" alt="image.png" style="zoom: 33%;" />
- 链表归并：参考 [21. 合并两个有序链表](https://leetcode-cn.com/problems/merge-two-sorted-lists/) ，有递归和迭代两种方法。

注意：

- 寻找中点时需要**保存慢指针的前一位置**，便于在找到中点时断开与前半部分链表的连接
- 迭代合并链表时需要创建虚拟头结点，**返回真实头结点**dummy->next。
- 因为创建了虚拟头结点，合并时只需要指针操作即可完成排序，因而不像数组归排中需要额外的长度为n的数组来存储合并结果，省去了O(n)的空间，但递归调用仍需O(logn)的空间，因而空间复杂度为O(logn)

```cpp
// 写法1
class Solution {
public:
    ListNode* sortList(ListNode* head) {
        if(!head || !head->next) return head;

        auto fast = head, slow = head, pre = head;
        while(fast && fast->next) {
            pre = slow;
            slow = slow->next;
            fast = fast->next->next;
        }
        pre->next = NULL; // 前半部分与后半部分断开连接
        
        return merge(sortList(head), sortList(slow));
    }

    ListNode* merge(ListNode* l1, ListNode* l2) {
        ListNode* dummy = new ListNode(-1); // 虚拟头结点

        ListNode* cur = dummy;
        while(l1 && l2) {
            if(l1->val <= l2->val) {
                cur->next = l1;
                l1 = l1->next;
            } else {
                cur->next = l2;
                l2 = l2->next;
            }
            cur = cur->next;
        }

        cur->next = l1 ? l1 : l2; // 处理未遍历完的节点
        return dummy->next; // 返回真实头结点
    }
};

// 写法2
class Solution {
public:
    ListNode* sortList(ListNode* head) {
        if(!head || !head->next) return head;

        auto fast = head, slow = head, pre = head;
        while(fast && fast->next) {
            pre = slow;
            slow = slow->next;
            fast = fast->next->next;
        }
        pre->next = NULL; // 前半部分与后半部分断开连接
        
        // 拆分
        auto l1 = sortList(head), l2 = sortList(slow);

        // 合并
        ListNode* dummy = new ListNode(-1); // 虚拟头结点
        ListNode* cur = dummy;
        while(l1 && l2) {
            if(l1->val <= l2->val) {
                cur->next = l1;
                l1 = l1->next;
            } else {
                cur->next = l2;
                l2 = l2->next;
            }
            cur = cur->next;
        }
        cur->next = l1 ? l1 : l2; // 处理未遍历完的节点

        return dummy->next; // 返回真实头结点
    }
};
```



[方法3](https://www.acwing.com/solution/LeetCode/content/408/)：自底向上归并排序-非递归，稳定，时间复杂度O(nlogn)，空间复杂度O(1)

```cpp

```

