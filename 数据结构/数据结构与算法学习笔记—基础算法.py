# 数据结构与算法学习笔记—基础算法

## 递归

例子：有n个台阶，每次可以下1个台阶或两个台阶，请问走n个台阶有多少种走法？

解法：这个问题求解可以分解为两个子问题：先下一个台阶或先下两个台阶，因此可以写出其递推公式：$f(n)=f(n-1)+f(n-2)$。该递推公式的终止条件为：$f(1)=1$，$f(2)=2$。根据上述3个公式，可以写出代码：

```python
def downstair(n):
    if n==1:
        return 1
    if n==2:
        return 2
    return downstair(n-1)+downstair(n-2)
```

这个例子的实现就是一个完整的递归代码实现。编写递归代码的关键是找到将大问题拆分为小问题的规律，根据规律编写递推公式，并确定终止条件，然后将递推公式与终止条件翻译为代码。拆分问题的关键是：只关注当前层次的拆分，将拆分后的问题假设为已解决的问题。

### 如何避免递归堆栈溢出问题？

每调用一个函数时，都会将临时变量封装为栈帧压入栈中，当函数执行完毕后，再出栈。因此当递归层次很深时，一直压入栈，会有堆栈溢出的风险。为了避免堆栈溢出，有两种解决方案：

- 限制递归层次

```python
def downstair(n):
	if n>1000:
		raise Exception
    if n==1:
        return 1
    if n==2:
        return 2
    return downstair(n-1)+downstair(n-2)
```

- 通过循环手动模拟入栈出栈(倒着算)将递归转换为非递归

```python
def downstair(n):
    if n==1:
        return 1
    if n==2:
        return 2
	pre=1
    prepre=2
    result=0
    for _ in range(3,n+1):
        result=pre+prepre
        pre,prepre=prepre,result
    return result
```

### 如何避免递归中重复计算问题？

递归运算中会有很多重复计算。

![递归重复计算]()

为了避免重复计算，可以通过一个散列表来存储已经求解过得数据。

```python
HAS_RESOLERD=dict()
def downstair(n):
    if n==1:
        return 1
    if n==2:
        return 2
    if n in HAS_RESOLERD:
        return HAS_RESOLERD.get(n)
    result = downstair(n-1)+downstair(n-2)
    HAS_RESOLERD[n]=result
    return result
```

## 排序

## 查找
