//改变调用顺序
int a;
int b;
int program(int a,int b,int c)
{
	int i;
	int j;
	i=0;
	if(a>(b+c))
	{
		j=a+(b*c+1);
	}
	else
	{
		j=a;       // 括号不匹配
	}
	return i;
}

int demo(int a)
{
	a=a+2;
	return a*2;
}

void main(void)
{
	int a;
	int b;
	int c;
	a=3;
	b=4;
	c=2;
	a=program(a,demo(c),b);   //改变demo调用顺序查看是否正确
	return;
}###