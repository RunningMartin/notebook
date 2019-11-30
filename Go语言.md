# Go语言

## 基本类型

### 类型与值

编程语言中的类型可以视作为值的模板，用于定义值的规格与限制；值是类型的实例。

大多数编程语言支持自定义类型和内置类型。值可以用字面形式表示，但处于阅读方便，推荐采用变量和有名常量表示。

Go语言中有名字的函数、值、类型等统称为资源，资源名必须为标识符。标识符要求只能有`Unicode`字母、数字和`_`(下划线)组成，并且只能以`Unicode`字母或`_`开头。`Unicode`字母由[`Unicode`标准](<https://unicodebook.readthedocs.io/unicode.html>)的`Lu`、`LI`、`Lt`、`Lm`和`Lo`分类组成；)，数字是`Nd`分类。Go语言中，关键字用于帮助编译器解释，因此标识符不能为关键字。

Go语言中将由[大写字母](<http://www.fileformat.info/info/unicode/category/Lu/list.htm>)开头的标识符视作为导出标识符，其他标识符视作为非导出标识符(私有)。

### 基本类型

- 布尔类型：`bool`，内置常量为`false`、`true`。
- 整型：
  - `int8`、`uint8`、`int16`、`uint16`、`int32`、`uint32`、`int64`、`uint64`：
  - `int`、`uint`：依赖于具体编译器实现，`64`位操作系统中为`64`位。
  - `uintptr`：依赖于具体编译器实现，用于存储内存地址。
  - `byte`：`uint8`的内置别名。
  - `rune`：`int32`的内置别名。
- 浮点类型：`float32`、`float64`。
- 复数：`complex64`(实数、虚数由`float32`组成)、`complex128`(实数、虚数由`float64`组成)
- 字符串：`string`

Go语言中可以使用类似`type status bool`的语句自定义类型，`status`和`bool`是两个不同的类型。

每个类型都有一个默认零值：

- 布尔类型：`false`
- 数值类型：`0`
- 字符串：空字符串`""`

### 基本类型的值的字面表示

- 布尔类型：`false`、`true`
- 整数：`0x`(十六进制)、`0b`(二进制)、`0|0o|0O`(八进制)
- 浮点数：`1.23`、`1.23E+2`(123.0)、`0x1p-2`(0.25，十六进制，特殊表示减法`0x15e - 2`)。
- 数字还可以用下划线分段，增强可读性：`6_9`(69)

### rune

`rune`是`int32`的别名，用于表示特殊的整型。Go中，`rune`表示一个`Unicode`码点，通常一个`Unicode`字符由一个码点组成，单也存在多个码点组成一个字符的情况。`rune`的字面量由单引号括起，字面量有三种表达方式：

- 直接使用`Unicode`字符：`'a'`
- 采用数字表示：`'\141'（八进制）`、`\x61（十六进制）`、`\u0061`、`\U00000061`都表示字符`a`。
- 转义字符：`'\n'（表示换行符）`

### 字符串字面表示形式

Go语言中，所有的字符串包括源代码都必须是`UTF-8`码。`UTF-8`中，一个英文字符用一个字节表示，一个中文用三个字节表示。

- 解释型字面表示：解释型用双引号括起，内部如果包含`rune`格式，则表示为相应的`Unicode`字符，但是不支持包含`\'`(`runn`支持`\'`，不支持`\"`)。
- 直白字面表示：直白型用反引号括起(左上角，数字`1`旁边)，内部不进行`Unicode`转换。为了兼容不同平台，直白型将忽视回车符(`ox0D`)。

```
"\141"=>表示字母串a
`\141`=>表示字符串\141
```

## 常量

Go语言中，各种内置类型的字面表示形式属于无名常量(字面常量) ，而`false`和`true`属于预声明的有名常量。

### 类型不确定的值和类型确定的值

Go中，有些值的类型是有很多种可能，这些值被称为类型不确定的值。对于大多数类型不确定的值来说，都有一个默认类型，但`nil`没有默认类型。大多数类型不确定的值都是字面常量或有名常量：

- 字符串字面值默认类型为`string`。
- 布尔字面值默认类型为`bool`。
- 整形串字面值默认类型为`int`。
- `rune`字面值默认类型为`rune`。
- 浮点数字面值默认类型为`float64`。
- 复数字面值默认类型为`complex128`。

类型不确定的值可以通过`T(v)`语法，显式将值`v`转换为指定类型`T`，但`T(v)`不是对所有的`v`都合法。

- `v`是一个可以表示为`T`类型的值（类型兼容，且数据在有效范围内）。
- `v`的默认类型是整数类型，`T`是字符串类型。转换时将`v`视作为`Unicode`码点的`UTF-8`形式，对于不合法的`Unicode`码点，结果等同于`"\uFFFD"`。

```go
// 合法
string(65) 		//"A"
string(-1)		//"\uFFFD"

int(1.23)		// 非法，1.23不能表示为int
uint(-8)		//非法，-8不能表示为uint
```

### 类型推断

在某些场景下，代码中使用了一些类型不确定的值，编译器能自动推断出在此场景下，该类型不确定的值的类型，主要适用于以下两个场景(类似隐式转换)：

- 此处需要特定类型的值且该类型不确定的值能表示为该类型的值，Go编译器将此类型不确定的值视作为特定类型的值。这种场景常出现在运算符运算、函数调用、赋值语句中。
- 某些场景对值没有特定的类型要求，Go编译器将该类型不确定的值只作为默认类型的类型确定值。

### 有名常量声明

有名常量必须为布尔、数值或字符串且常量名必须遵守资源命名规则。Go中，使用关键字`const`声明一个有名常量。常量声明中`=`代表绑定，每个声明都是将字面常量绑定到对应的字面常量。常量声明中可以加入类型，用于声明类型确定的常量，但常量的值必须满足指定类型的要求，否则会编译报错。

```go
package main
//声明单个有名常量
const π = 3.1416
const Pi = π	// Pi和π是两个单独的有名常量，只是值相等

// 声明一组有名常量
const (
	YES = true
    No =! YES
)

// 声明类型确定的有名常量
const X float64 = 3.14
const (
	A,B int32 = -3,5
)
// 或者
const X = float64(3.14)
const (
    A,B = int(-3),int(5)
)

// 表示uint的最大值
//不能使用const MAX_UINT unit=(1<<64)-1，在32位系统中非法。
const MAX_UINT = ^uint(0)
// int最大值
const MAX_INT = int(^uint(0)>>1)
//判断操作系统位数
// 如果是64位操作系统，uint最大值右移63为为1，否则为0
// 32<<1 == 32*2  32<<0 == 32*1
const NativeWordBits = 32 << (^uint(0)>>63)
// 64位操作系统中，uint最大值右移63为为1
const Is64BitOS = (^uint(0)>>63 == 1)
// 32位操作系统中，uint最大值右移31位为1
const Is32BitOS= (^uint(0)>>31== 1)
```

### 常量声明的自动补全

在一个包含多个常量描述的常量声明中，除了第一个常量描述以外，后续常量描述可以只有标识符，Go编译器将通过照搬前一个完整的常量描述进行补全。

```go
const (
	X float32 = 3.14
    Y
    Z
    A,B = "GO","Language"
    C,_
)
// 自动补全后
const (
	X float32 = 3.14
    Y float32 = 3.14
    Z float32 = 3.14
    A,B = "GO","Language"
    C,_ = "GO","Language"
)
```

### iota

`Go`中预声明了一个特殊的有名常量`iota`，它的值预声明为`0`。在编译过程中，如果`iota`出现在常量声明中，它的值表示第`n`个常量描述符(从`0`开始)。

```go
package main

func main(){
    const (
    	k = 3					// iota=0
        m float32 = iota +0.5 	// m=1.5,iota=1
        n						// n=2.5,iota=2
    )
    const x=iota				//x=0 iota=0

	println("k:",k)
	println("m:",m)
	println("n:",n)
	println("x:",x)
}
```

## 变量

### 变量声明

变量是运行时刻存储在内存中并且可以被更改的有名字的值。每一个变量都是类型确定的值，因此声明变量时必须提供足够多的信息，以便于编译器推断出变量的类型。

变量有两种声明方式

- 标准声明：标准声明的格式为`var 变量名 类型 = 初始化值`，并且在一条声明语句中，可以声明多个同类型变量。

  ```go
  package main
  
  import (
      "fmt"
      "reflect"
  )
  
  func main() {
      //var website string = "https://golang.site"
  	//var compiled, dynamic bool = true, false
      // 省略变量类型，编译器更佳初始值推断变量类型
      var website, dynamic = "https://golang.site", false
      // website的初始类型为string
      // dynamic的初始类型为false
      fmt.Println(website," type:", reflect.TypeOf(website))
  	fmt.Println(dynamic," type:", reflect.TypeOf(dynamic))
      
      // 忽略初始值，编译器将初始值设置为零值
      var compiled bool
      fmt.Println("compiled"," init value:", compiled)
  	// 声明多个变量
  	var(
  	lang, bornYear = "GO",2007
  	)
      fmt.Println(lang,bornYear)
  }
  ```

- 短声明：短声明只能用于声明局部变量，短声明的语法为`变量名 := 变量值`。

  ```go
  package main
  
  import (
      "fmt"
      "reflect"
  )
  
  func main() {
      lang, bornYear := "Go", 2007
      fmt.Println("lang",lang,"type", reflect.TypeOf(lang))
  	fmt.Println("bornYear:",bornYear,"type", reflect.TypeOf(bornYear))
  }
  ```

- 赋值语句：一个变量声明后，可以通过`表达式 = 值`进行赋值。表达式必须为一个可寻址的值、映射元素或一个空标识符`_`。常量是不可改变的，因此不能作为表达式。

## 作用域

变量或常量的作用域决定了该标识符的可见范围，常见的作用域有：

- 全局变量、全局常量：作用域为整个代码包。
- 局部变量、局部常量：作用域开始于定义位置，接受于所在代码块的结尾。

## 运算操作符



## 扩展

- 获取数据类型：`reflect.TypeOf(x)`需要导入`reflect`。

  ```go
  package main
  
  import (
      "fmt"
      "reflect"
  )
  
  func main() {
      //var website string = 'https://golang.site'
  	//var compiled, dynamic bool = true, false
      // 省略变量类型，编译器更佳初始值推断变量类型
      var website, dynamic = 'https://golang.site', false
      // website的初始类型为string
      // dynamic的初始类型为false
      fmt.Println(website," type:", reflect.TypeOf(website))
  	fmt.Println(dynamic," type:", reflect.TypeOf(dynamic))
  }
  ```
