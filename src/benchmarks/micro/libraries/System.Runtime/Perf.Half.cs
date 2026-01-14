// Licensed to the .NET Foundation under one or more agreements.
// The .NET Foundation licenses this file to you under the MIT license.
// See the LICENSE file in the project root for more information.

using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

using BenchmarkDotNet.Attributes;

using MicroBenchmarks;

namespace System.Tests
{
    [BenchmarkCategory(Categories.Libraries)]
    public class Perf_Half
    {
        private const int LoopCount = 1000;

        public static IEnumerable<Half> Values => new Half[]
        {
            BitConverter.UInt16BitsToHalf(0x03ff),  //Maximum subnormal number in Half
            (Half)12345.0f /* same value used by other tests to compare the perf */,
            BitConverter.UInt16BitsToHalf(0x7dff)   //NaN
        };

        public static IEnumerable<float> SingleValues => new float[]
        {
            6.097555E-05f,
            12345.0f /* same value used by other tests to compare the perf */,
            65520.0f,   //Minimum value that is infinity in Half
            float.NaN
        };

        public static IEnumerable<object[]> DoubleValues() 
        {
            yield return new object[] { BitConverter.UInt16BitsToHalf(0x03ff), BitConverter.UInt16BitsToHalf(0x03ff) };  //Maximum subnormal number in Half;
            yield return new object[] { (Half)12345.0f, (Half)12345.0f }; /* same value used by other tests to compare the perf */
            yield return new object[] { BitConverter.UInt16BitsToHalf(0x7dff), BitConverter.UInt16BitsToHalf(0x7dff) };   //NaN
        }

        [Benchmark(OperationsPerInvoke = LoopCount)]
        [ArgumentsSource(nameof(SingleValues))]
        public Half SingleToHalf(float value)
        {
            Half result = default;
            for (int i = 0; i < LoopCount; i++)
            {
                result = (Half)value;
            }
            return result;
        }

        [Benchmark(OperationsPerInvoke = LoopCount)]
        [ArgumentsSource(nameof(Values))]
        public float HalfToSingle(Half value)
        {
            float result = default;
            for (int i = 0; i < LoopCount; i++)
            {
                result = (float)value;
            }
            return result;
        }

        [Benchmark(OperationsPerInvoke = LoopCount)]
        [ArgumentsSource(nameof(Values))]
        public Half HalfAddition(Half left, Half right)
        {
            Half result = default;
            for (int i = 0; i < LoopCount; i++)
            {
                result = left + right;
            }
            return result;
        }

        [Benchmark(OperationsPerInvoke = LoopCount)]
        [ArgumentsSource(nameof(Values))]
        public Half HalfSubtraction(Half left, Half right)
        {
            Half result = default;
            for (int i = 0; i < LoopCount; i++)
            {
                result = left - right;
            }
            return result;
        }

        [Benchmark(OperationsPerInvoke = LoopCount)]
        [ArgumentsSource(nameof(Values))]
        public Half HalfMultiplication(Half left, Half right)
        {
            Half result = default;
            for (int i = 0; i < LoopCount; i++)
            {
                result = left * right;
            }
            return result;
        }

        [Benchmark(OperationsPerInvoke = LoopCount)]
        [ArgumentsSource(nameof(Values))]
        public Half HalfDivision(Half left, Half right)
        {
            Half result = default;
            for (int i = 0; i < LoopCount; i++)
            {
                result = left / right;
            }
            return result;
        }

        [Benchmark(OperationsPerInvoke = LoopCount)]
        [ArgumentsSource(nameof(Values))]
        public Half HalfNegation(Half value)
        {
            Half result = default;
            for (int i = 0; i < LoopCount; i++)
            {
                result = -value;
            }
            return result;
        }

        [Benchmark(OperationsPerInvoke = LoopCount)]
        [ArgumentsSource(nameof(Values))]
        public bool HalfEquals(Half left, Half right)
        {
            bool result = default;
            for (int i = 0; i < LoopCount; i++)
            {
                result = left == right;
            }
            return result;
        }

        [Benchmark(OperationsPerInvoke = LoopCount)]
        [ArgumentsSource(nameof(Values))]
        public bool HalfNotEquals(Half left, Half right)
        {
            bool result = default;
            for (int i = 0; i < LoopCount; i++)
            {
                result = left != right;
            }
            return result;
        }

        [Benchmark(OperationsPerInvoke = LoopCount)]
        [ArgumentsSource(nameof(Values))]
        public bool HalfLessThan(Half left, Half right)
        {
            bool result = default;
            for (int i = 0; i < LoopCount; i++)
            {
                result = left < right;
            }
            return result;
        }

        [Benchmark(OperationsPerInvoke = LoopCount)]
        [ArgumentsSource(nameof(Values))]
        public bool HalfLessThanOrEqual(Half left, Half right)
        {
            bool result = default;
            for (int i = 0; i < LoopCount; i++)
            {
                result = left <= right;
            }
            return result;
        }

        [Benchmark(OperationsPerInvoke = LoopCount)]
        [ArgumentsSource(nameof(Values))]
        public bool HalfGreaterThan(Half left, Half right)
        {
            bool result = default;
            for (int i = 0; i < LoopCount; i++)
            {
                result = left > right;
            }
            return result;
        }

        [Benchmark(OperationsPerInvoke = LoopCount)]
        [ArgumentsSource(nameof(Values))]
        public bool HalfGreaterThanOrEqual(Half left, Half right)
        {
            bool result = default;
            for (int i = 0; i < LoopCount; i++)
            {
                result = left >= right;
            }
            return result;
        }
    }
}
