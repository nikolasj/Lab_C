#define _CRT_SECURE_NO_WARNINGS

#include <iostream> 
#include <stdlib.h>
#include <stdio.h>
#include <string>
#include "point.h"

using namespace std;
using Program::point;
ostream& operator << (ostream& out, point* a)
{
	out << a->getC() << ": " << a->getX() << "," << a->getY() << " " << endl;
	return out;
}

ostream& operator << (ostream& out, array_point* a)
{
	int n = a->getN();
	if (n > 50) n = 50;
	for (int i = 0; i < n; i++)
	{
		point p = a->getPointByIndex(i);
		out << p.getC() << ": " << p.getX() << "," << p.getY() << " " << endl;
	}
	return out;
}
int main()
{
	setlocale(LC_ALL, "rus");
	char l; double a, b, d;
	char*s = new char[10];

	array_point* arr = new array_point(5);
	arr->init();
	cout << arr;

	/*

	cout << "¬веди значение координаты х" << endl;
	cin >> a;
	cout << endl;
	cout << "¬веди значение координаты y" << endl;
	cin >> b;
	cout << endl;
	cout << "¬веди название точки" << endl;
	cin >> s;
	point* p4 = new point(a, b, s);
	p4->print();*/
	cin >> l;
	return 0;
}