https://blog.csdn.net/dkjkls/article/details/88933950
# Pycharm自定义函数模板快捷方式

- setting->live Templates：新建模板

- 输入模板：Template Text

```
"""功能描述：
    Args:
        $arg$($type$):$description$ 
    Returns:
        $return$:$return_description$ 
    Raises:
        $exception$
    Examples:
        $example$
    Notes:
        $note$
    Changes:
        $USER$ created by $DATE$ $TIME$
"""
```

- 配置变量
- 配置指定语言：
- 保存后，在相应位置输入`fmt`回车，然后根据光标依次填入相应参数即可。
