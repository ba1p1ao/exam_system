<template>
  <div class="score-trend-chart">
    <div ref="chartRef" style="width: 100%; height: 400px;"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getScoreTrendChart } from '@/api/chart'

const chartRef = ref(null)
let chartInstance = null

const props = defineProps({
  days: {
    type: Number,
    default: 30
  }
})

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)

  const option = {
    title: {
      text: '成绩趋势图',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const data = params[0]
        return `${data.name}<br/>${data.seriesName}: ${data.value}分`
      }
    },
    xAxis: {
      type: 'category',
      data: [],
      axisLabel: {
        rotate: 45
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
        name: '考试成绩',
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
      }
    ]
  }

  chartInstance.setOption(option)
}

const loadData = async () => {
  try {
    const res = await getScoreTrendChart(props.days)

    if (res.code === 200 && res.data) {
      const trendList = res.data.trend || []

      if (trendList.length === 0) {
        chartInstance.setOption({
          title: {
            text: '暂无考试成绩记录'
          },
          xAxis: {
            data: []
          },
          series: [
            {
              data: []
            }
          ]
        })
        return
      }

      const dates = trendList.map(item => {
        const date = new Date(item.date)
        return `${date.getMonth() + 1}/${date.getDate()}`
      })
      const scores = trendList.map(item => item.score)

      chartInstance.setOption({
        title: {
          text: '成绩趋势图'
        },
        xAxis: {
          data: dates
        },
        series: [
          {
            data: scores
          }
        ]
      })
    } else {
      ElMessage.error('加载成绩趋势数据失败')
    }
  } catch (error) {
    console.error('加载成绩趋势数据失败:', error)
    chartInstance.setOption({
      title: {
        text: '加载数据失败'
      }
    })
  }
}

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

onMounted(() => {
  initChart()
  loadData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  window.removeEventListener('resize', handleResize)
})

const refresh = () => {
  loadData()
}

defineExpose({
  refresh
})
</script>

<style scoped>
.score-trend-chart {
  width: 100%;
}
</style>