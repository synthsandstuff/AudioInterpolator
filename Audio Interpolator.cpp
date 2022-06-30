#include <tgmath.h>

#define len 256

class Interpolation
{
    public:

    int interpolation_Factor;
    float interpolation_Fraction;

    private:
    int* Indexer(int k, int audio[len])
    {
        int indx[4];
        indx[1] = audio[k];
        if(k)
        {
            indx[0] = audio[k-1];
        }
        else
        {
            indx[0] = 0;
        }
        if(k+1>len)
        {
            indx[2] = audio[k+1];
        }
        else
        {
            indx[2] = 0;
        }
        if(k+2>len)
        {
            indx[3] = audio[k+2];
        }
        else
        {
            indx[3] = 0;
        }
        return indx;
    };

    int Interpolate1(int x0, int x1, int x2, int x3, float t)
    {
        float c0 = x1;
        float c1 = 0.5 * (x2 - x0);
        float c2 = x0 - (2.5 * x1) + (2 * x2) - (0.5 * x3);
        float c3 = (0.5 * (x3 - x0)) + (1.5 * (x1 - x2));
        return round((((((c3 * t) + c2) * t) + c1) * t) + c0);
    };

    int Interpolate2(int x0, int x1, int x2, int x3, float t)
    {
        float c0 = x3 - x2 - x0 + x1;
        float c1 = x0 - x1 - c0;
        float c2 = x2 - x0;
        float c3 = x1;
        return round((c0 * (t * t * t)) + (c1 * (t * t)) + (c2 * t) + c3);
    };

    int Interpolate3(int x0, int x1, int x2, int x3, float t)
    {
        return round(((x1*1-t)+(x2*t))/2);
    };

    int Interpolate4(int x0, int x1, int x2, int x3, float t)
    {
        return round(x1);
    };
};