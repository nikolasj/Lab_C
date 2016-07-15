#pragma once

namespace Program
{
	class point
	{
		double x, y;
		char *c;
		// new text
                // new text2
                // new text3	
	public:
		point();
		point(double a, double b, char* d);
		point(point* a);
		~point();
		point operator=(point t);
		void setX(double a);
		void setY(double b);
		void setC(char *p);
		double point::getX()
		{
			return x;
		}
		double getY()
		{
			return y;
		}
		char* getC()
		{
			return c;
		}
		void init(double a, double b);
		void print();
	};
	
}

