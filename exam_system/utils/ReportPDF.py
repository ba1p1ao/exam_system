import os
import io
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class ReportPDFGenerator:
    """考试分析报告 PDF 生成器"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._register_chinese_font()
        self._setup_custom_styles()

    def _register_chinese_font(self):
        """注册中文字体"""
        # 尝试注册系统中文字体
        font_paths = [
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',  # Linux Noto Sans CJK
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',           # Linux 文泉驿微米黑
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',             # Linux 文泉驿正黑
            '/System/Library/Fonts/PingFang.ttc',                       # macOS 苹方
            'C:/Windows/Fonts/msyh.ttc',                                # Windows 微软雅黑
            'C:/Windows/Fonts/simhei.ttf',                              # Windows 黑体
        ]

        font_registered = False
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                    font_registered = True
                    break
                except Exception as e:
                    continue

        if not font_registered:
            # 如果找不到系统字体，尝试使用项目中的字体
            project_font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'chinese.ttf')
            if os.path.exists(project_font_path):
                try:
                    pdfmetrics.registerFont(TTFont('ChineseFont', project_font_path))
                    font_registered = True
                except Exception as e:
                    pass

        if not font_registered:
            # 如果都找不到，使用 ASCII 字符替代（会有警告）
            pass

    def _setup_custom_styles(self):
        """设置自定义样式"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='ChineseFont'
        )

        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='ChineseFont'
        )

        # 修改默认样式的字体
        self.styles['Normal'].fontName = 'ChineseFont'
        self.styles['Heading1'].fontName = 'ChineseFont'
        self.styles['Heading2'].fontName = 'ChineseFont'
        self.styles['Heading3'].fontName = 'ChineseFont'

    def generate_exam_report(self, exam_title, summary, question_analysis, recommendations):
        """
        生成考试分析报告 PDF

        Args:
            exam_title (str): 试卷标题
            summary (dict): 考试摘要数据
            question_analysis (list): 题目分析数据
            recommendations (list): 教学建议列表

        Returns:
            BytesIO: PDF 文件的字节流
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                               rightMargin=30, leftMargin=30,
                               topMargin=30, bottomMargin=18)
        elements = []

        # 标题
        title = Paragraph("考试分析报告", self.title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))

        # 试卷信息
        exam_title_para = Paragraph(f"<b>试卷名称：</b>{exam_title}", self.styles['Normal'])
        elements.append(exam_title_para)
        elements.append(Spacer(1, 6))

        # 生成时间
        from django.utils import timezone
        generate_time = Paragraph(f"<b>生成时间：</b>{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal'])
        elements.append(generate_time)
        elements.append(Spacer(1, 20))

        # 考试摘要
        elements.append(Paragraph("一、考试摘要", self.heading_style))
        summary_data = [
            ['统计项', '数值'],
            ['参与人数', str(summary.get('total_participants', 0))],
            ['平均分', f"{summary.get('average_score', 0):.2f}"],
            ['最高分', f"{summary.get('highest_score', 0):.2f}"],
            ['最低分', f"{summary.get('lowest_score', 0):.2f}"],
            ['及格率', f"{summary.get('pass_rate', 0):.2%}"],
        ]
        summary_table = Table(summary_data, colWidths=[80, 80])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        # 题目分析
        elements.append(Paragraph("二、题目分析", self.heading_style))
        question_data = [['题目ID', '难度', '正确率']]
        difficulty_map = {'easy': '简单', 'medium': '中等', 'hard': '困难'}

        for qa in question_analysis:
            qid = qa.get('question_id', '')
            qcr = qa.get('correct_rate', 0)
            qdl = qa.get('difficulty_level', 'medium')

            question_data.append([
                str(qid),
                difficulty_map.get(qdl, qdl),
                f"{qcr:.2%}"
            ])

        question_table = Table(question_data, colWidths=[60, 60, 60])
        question_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (2, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        elements.append(question_table)
        elements.append(Spacer(1, 20))

        # 教学建议
        elements.append(Paragraph("三、教学建议", self.heading_style))
        for i, rec in enumerate(recommendations, 1):
            elements.append(Paragraph(f"{i}. {rec}", self.styles['Normal']))
            elements.append(Spacer(1, 6))

        # 构建文档
        doc.build(elements)
        buffer.seek(0)
        return buffer

    def save_pdf(self, buffer, filename):
        """
        保存 PDF 文件到服务器

        Args:
            buffer (BytesIO): PDF 文件的字节流
            filename (str): 文件名

        Returns:
            str: 文件保存的完整路径
        """
        # 创建报告目录
        report_dir = os.path.join(settings.BASE_DIR, 'static', 'report_pdfs')
        os.makedirs(report_dir, exist_ok=True)

        filepath = os.path.join(report_dir, filename)

        with open(filepath, 'wb') as f:
            buffer.seek(0)
            f.write(buffer.read())

        return filepath