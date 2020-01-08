# Python小技巧

## 快速生成依赖文件

`Python`通过`requirements.txt`来管理项目所依赖的库，通过`pip install -r requirements.txt`命令可以直接安装项目所需要的依赖文件。

常见的`requirements.txt`生成方法由两种

- 原生`pip`工具`pip freeze > requirements.txt`，这种方法会将当前环境中所安装的库全部导出，即使你在项目中没有使用，只是之前实验时安装的依赖库。
- 第三方工具`pipreqs requirements.txt --encoding=utf-8`，该工具使用前需要安装`pip install pipreqs`，`pipreqs`的优点它会扫描项目的依赖，只导出使用的依赖；`pipreqs`还可以指定扫描目录`pipreqs ./ --encoding=utf-8`。

## 文件路径处理

`Python`中常见的文件路径处理方式是通过`os.path`进行处理。

```python
In[2]: import os
# 获取当前目录的绝对路径
In[3]: os.path.abspath('./')
Out[3]: 'D:\\Work\\CommonTools'
# 进行路径拼接
In[4]: os.path.join(os.path.abspath('./'),'new_file.py')
Out[4]: 'D:\\Work\\CommonTools\\new_file.py'
# 获取父目录
In[5]: os.path.abspath(os.path.dirname(os.getcwd()))
Out[5]: 'D:\\Work'
# 获取文件后缀名
In[6]: os.path.splitext('new_file.py')[-1]
Out[6]: '.py'
```

`os.path`处理文件路径时，比较复杂、难用，因此可以使用`pathlib`替代`os.path`。

```python
In[2]: import pathlib
# 获取当前目录的绝对路径
In[3]: path = pathlib.Path('./')
In[4]: path=path.absolute()
In[5]: path.as_posix()
Out[5]: 'D:/Work/CommonTools'
# 进行路径拼接
In[6]: file_path = path / 'new_file.py'
In[7]: file_path.as_posix()
Out[7]: 'D:/Work/CommonTools/new_file.py'
# 获取父目录
In[8]: path.parent
Out[8]: WindowsPath('D:/Work')
# 获取文件后缀名
In[9]: file_path.suffix
Out[9]: '.py'
# 列出当前目录下的py文件
In[13]: list(path.glob('*.py'))
Out[13]: [WindowsPath('D:/Work/CommonTools/tools.py')]
```

更多`os.pah`库和`pathlib`库的方法对照，请查看[官方文档](https://docs.python.org/3/library/pathlib.html#correspondence-to-tools-in-the-os-module)。

## 通过set将对象去重

通过`set`将对象去重要求对象必须实现三个方法：

- `__eq__`：判断两个对象是否相等。
- `__ne__`：判断两个对象是否不等。
- `__hash__`：生成对象的`hash`值。

`set`内部可以视作为字典，以对象的`hash`值作为键，通过`hash`来判断对象是否重复。但是`hash`值可能出现冲突，因此还需在`hash`值相同时，对比两个对象是否相等，这也是为什么需要实现这三个方法的原因。

```python
In[2]: class Person(object):
   ...:    def __init__(self, name, age):
   ...:        self._name = name
   ...:        self._age = age
   ...:
   ...:    def __eq__(self, other):
   ...:        if isinstance(other, Person):
   ...:            return (self._name == other._name) and (self._age == other._age)
   ...:        else:
   ...:            return False
   ...:
   ...:    def __ne__(self, other):
   ...:        return not self.__eq__(other)
   ...:
   ...:    def __hash__(self):
   ...:        return hash(self._name + str(self._age))
   ...:
   ...:    def __repr__(self):
   ...:        return f'{self._name}:{self._age}'
   ...:    
In[3]: p1 = Person('martin', 24)
   ...:p2 = Person('martin', 24)
In[4]: set([p1, p2])
Out[4]: {martin:24}
In[5]: p2 = Person('martin', 25)
In[6]: set([p1, p2])
Out[6]: {martin:24, martin:25}
```

## 单元测试`unitest`捕获异常

单元测试`unitest`中提供了两个方法用于捕获异常，判断异常信息是否符合预期：

- `assertRaises()`：只支持指定异常判断。
- `assertRaisesRegex(异常类型,异常信息正则表达式,测试方法,参数)`：支持匹配异常信息。

```python
import unittest

def divide_exactly(a, b):
    return a // b

class MyTestCase(unittest.TestCase):
    def test_division(self):
        self.assertEqual(divide_exactly(6, 6), 1)
        
		# 捕获指定异常
        self.assertRaises(ZeroDivisionError, divide_exactly, 5, 0)
		# 可以作为上下文管理器使用
        with self.assertRaises(ZeroDivisionError):
            divide_exactly(5, 0)
            
		# 捕获指定异常
        self.assertRaisesRegex(ZeroDivisionError, 'integer division or modulo by zero', divide_exactly, 5, 0)
		# 可以作为上下文管理器使用
        with self.assertRaisesRegex(ZeroDivisionError, 'integer division or modulo by zero'):
            divide_exactly(5, 0)


if __name__ == '__main__':
    unittest.main()
```

