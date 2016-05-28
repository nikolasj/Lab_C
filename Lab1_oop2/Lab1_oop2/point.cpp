#define _CRT_SECURE_NO_WARNINGS
#include "point.h"
#include <iostream> 
#include <string>
#include <stdlib.h>
#include <stdio.h>


using namespace std;

namespace Program
{
	point::point(point* a)
	{
		x = a->x;
		y = a->x;
		strncpy(c, a->c, 10);
	}
	point::point(double a, double b, char* d)
	{
		x = a;
		y = b;
		strncpy(c, d, 10);
		//strcpy(c, 10, d);
	}
	point::point()
	{
		x = 0;
		y = 0;
		c = new char[10];
		//c[0] = '\0';
	}
	point::~point()
	{
		delete c;
	}
	point point::operator=(point t)
	{
		x = t.x;
		y = t.y;
		strncpy(c, t.c, 10);
		return *this;
	}
	void point::setX(double a)
	{
		x = a;
	}
	void point::setY(double a)
	{
		y = a;
	}
	void point::setC(char* d)
	{
		strncpy(c, d, 10);
	}
	void point::init(double a, double b)
	{
		x = a;
		y = b;
	}
	void point::print()
	{
		cout << c << ": " << x << "," << y << " " << endl;
	}
}