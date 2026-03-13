<template>
  <div class="student-score-comparison-chart">
    <div ref="chartRef" style="width: 100%; height: 450px;"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getStudentScoreComparisonChart } from '@/api/chart'

const chartRef = ref(null)
let chartInstance = null
let resizeObserver = null
let dataLoaded = false

const initChart = () => {
  if (!chartRef.value) return

  // 确保 DOM 元素有宽度和高度
  const container = chartRef.value
  if (container.clientWidth === 0 || container.clientHeight === 0) {
    console.warn('图表容器尺寸为0，等待容器渲染')
    return
  }

  try {
    chartInstance = echarts.init(container)

    // 设置初始空配置
    const option = {
      title: {
        text: '学生成绩对比图',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        formatter: function(params) {
          let result = params[0].name + '<br/>'
          params.forEach(item => {
            result += `${item.marker}${item.seriesName}: ${item.value}分<br/>`
          })
          return result
        }
      },
      legend: {
        data: ['我的成绩', '班级平均'],
        top: 30
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: [],
        axisLabel: {
          rotate: 45,
          interval: 0,
          width: 100,
          overflow: 'truncate',
          ellipsis: '...'
        }
      },
      yAxis: {
        type: 'value',
        name: '分数',
        min: 0,
        max: 100
      },
      series: [
        {
          name: '我的成绩',
          type: 'line',
          data: [],
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          itemStyle: {
            color: '#409EFF'
          },
          lineStyle: {
            width: 3
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                {
                  offset: 0,
                  color: 'rgba(64, 158, 255, 0.3)'
                },
                {
                  offset: 1,
                  color: 'rgba(64, 158, 255, 0.05)'
                }
              ]
            }
          }
        },
        {
          name: '班级平均',
          type: 'line',
          data: [],
          smooth: true,
          symbol: 'diamond',
          symbolSize: 8,
          itemStyle: {
            color: '#67C23A'
          },
          lineStyle: {
            width: 3,
            type: 'dashed'
          }
        }
      ]
    }

    chartInstance.setOption(option)

    // 图表初始化成功后加载数据
    if (!dataLoaded) {
      loadData()
      dataLoaded = true
    }
  } catch (error) {
    console.error('图表初始化失败:', error)
  }
}

const loadData = async () => {
  if (!chartInstance) {
    console.warn('图表实例未初始化，无法加载数据')
    return
  }

  try {
    const res = await getStudentScoreComparisonChart()

    if (res.code === 200 && res.data) {
      const { my_scores, class_average, exam_titles } = res.data

      if (!my_scores || my_scores.length === 0 || !exam_titles || exam_titles.length === 0) {
        // 清空图表，显示"暂无数据"
        chartInstance.clear()
        chartInstance.setOption({
          title: {
            text: '暂无考试成绩记录',
            left: 'center',
            top: 'center',
            textStyle: {
              fontSize: 16,
              color: '#999'
            }
          },
          grid: {
            show: false
          },
          xAxis: {
            show: false
          },
          yAxis: {
            show: false
          },
          series: []
        })
        return
      }

      // 有数据时，清除之前的配置并重新设置（使用 notMerge: true 强制不合并）
      chartInstance.clear()
      chartInstance.setOption({
        title: {
          text: '学生成绩对比图',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            let result = params[0].name + '<br/>'
            params.forEach(item => {
              result += `${item.marker}${item.seriesName}: ${item.value}分<br/>`
            })
            return result
          }
        },
        legend: {
          data: ['我的成绩', '班级平均'],
          top: 30
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: exam_titles || [],
          axisLabel: {
            rotate: 45,
            interval: 0,
            width: 100,
            overflow: 'truncate',
            ellipsis: '...'
          }
        },
        yAxis: {
          type: 'value',
          name: '分数',
          min: 0,
          max: 100
        },
        series: [
          {
            name: '我的成绩',
            type: 'line',
            data: my_scores || [],
            smooth: true,
            symbol: 'circle',
            symbolSize: 8,
            itemStyle: {
              color: '#409EFF'
            },
            lineStyle: {
              width: 3
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: 'rgba(64, 158, 255, 0.3)'
                  },
                  {
                    offset: 1,
                    color: 'rgba(64, 158, 255, 0.05)'
                  }
                ]
              }
            }
          },
          {
            name: '班级平均',
            type: 'line',
            data: class_average || [],
            smooth: true,
            symbol: 'diamond',
            symbolSize: 8,
            itemStyle: {
              color: '#67C23A'
            },
            lineStyle: {
              width: 3,
              type: 'dashed'
            }
          }
        ]
      }, true) // 第二个参数 true 表示不合并，完全替换
    } else {
      // 加载失败
      chartInstance.clear()
      chartInstance.setOption({
        title: {
          text: '加载数据失败',
          left: 'center',
          top: 'center',
          textStyle: {
            fontSize: 16,
            color: '#999'
          }
        },
        grid: {
          show: false
        },
        xAxis: {
          show: false
        },
        yAxis: {
          show: false
        },
        series: []
      })
    }
  } catch (error) {
    console.error('加载成绩对比数据失败:', error)
    // 异常情况
    if (chartInstance) {
      chartInstance.clear()
      chartInstance.setOption({
        title: {
          text: '加载数据失败',
          left: 'center',
          top: 'center',
          textStyle: {
            fontSize: 16,
            color: '#999'
          }
        },
        grid: {
          show: false
        },
        xAxis: {
          show: false
        },
        yAxis: {
          show: false
        },
        series: []
      })
    }
  }
}

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

onMounted(() => {
  // 使用 ResizeObserver 监听容器尺寸变化
  resizeObserver = new ResizeObserver((entries) => {
    for (let entry of entries) {
      const { width, height } = entry.contentRect
      if (width > 0 && height > 0 && !chartInstance) {
        initChart()
      }
    }
  })

  if (chartRef.value) {
    resizeObserver.observe(chartRef.value)
  }

  // 初始尝试初始化
  initChart()

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
  window.removeEventListener('resize', handleResize)
})

const refresh = () => {
  dataLoaded = false
  loadData()
}

defineExpose({
  refresh
})
</script>

<style scoped>
.student-score-comparison-chart {
  width: 100%;
}
</style>