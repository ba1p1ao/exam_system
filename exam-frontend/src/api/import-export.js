import request from "@/utils/request";
import * as XLSX from "xlsx";

// 下载题目导入模板
export const downloadImportTemplate = () => {
  // 直接使用前端生成模板
  return generateTemplateFile();
};

// 前端生成Excel模板文件
const generateTemplateFile = () => {
  return new Promise((resolve) => {
    // 创建工作簿
    const wb = XLSX.utils.book_new();

    // 创建数据
    const data = [
      {
        题目类型: "单选题",
        题目分类: "数学",
        题目内容: "1+1等于多少？",
        选项A: "1",
        选项B: "2",
        选项C: "3",
        选项D: "4",
        正确答案: "B",
        题目解析: "1+1=2",
        难度: "easy",
        分值: 5,
      },
      {
        题目类型: "多选题",
        题目分类: "数学",
        题目内容: "以下哪些是偶数？",
        选项A: "1",
        选项B: "2",
        选项C: "3",
        选项D: "4",
        正确答案: "B,D",
        题目解析: "2和4是偶数",
        难度: "medium",
        分值: 10,
      },
      {
        题目类型: "判断题",
        题目分类: "常识",
        题目内容: "地球是圆的",
        选项A: "",
        选项B: "",
        选项C: "",
        选项D: "",
        正确答案: "A",
        题目解析: "地球是圆的",
        难度: "easy",
        分值: 5,
      },
      {
        题目类型: "填空题",
        题目分类: "语文",
        题目内容: "床前明月光，疑是____霜",
        选项A: "",
        选项B: "",
        选项C: "",
        选项D: "",
        正确答案: "地上",
        题目解析: "李白《静夜思》",
        难度: "easy",
        分值: 5,
      },
    ];

    // 创建工作表
    const ws = XLSX.utils.json_to_sheet(data);

    // 设置列宽
    ws["!cols"] = [
      { wch: 10 }, // 题目类型
      { wch: 10 }, // 题目分类
      { wch: 40 }, // 题目内容
      { wch: 15 }, // 选项A
      { wch: 15 }, // 选项B
      { wch: 15 }, // 选项C
      { wch: 15 }, // 选项D
      { wch: 15 }, // 正确答案
      { wch: 30 }, // 题目解析
      { wch: 10 }, // 难度
      { wch: 8 }, // 分值
    ];

    // 添加工作表到工作簿
    XLSX.utils.book_append_sheet(wb, ws, "题目导入模板");

    // 生成Excel文件
    const excelBuffer = XLSX.write(wb, { bookType: "xlsx", type: "array" });

    // 创建Blob
    const blob = new Blob([excelBuffer], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });

    resolve(blob);
  });
};

// 批量导入题目
export const importQuestions = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return request({
    url: "/question/import/",
    method: "post",
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

// 导出题目
export const exportQuestions = (data) => {
  return request({
    url: "/question/export/",
    method: "post",
    data,
    responseType: "blob",
  });
};

// 导出错题本
export const exportMistakeQuestions = () => {
  return request({
    url: "/mistake/export/",
    method: "post",
    responseType: "blob",
  });
};
