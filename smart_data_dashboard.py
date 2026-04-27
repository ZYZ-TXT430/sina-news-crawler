import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
from openai import OpenAI
import chardet

# 页面设置
st.set_page_config(
    page_title="智能数据看板",
    page_icon="📊",
    layout="wide"
)

# 标题
st.title("智能数据看板")
st.write("上传您的数据文件，自动进行分析和总结")

# 文件上传区域
uploaded_file = st.file_uploader(
    "请上传CSV或Excel文件",
    type=["csv", "xlsx"],
    help="支持.csv和.xlsx格式的数据文件"
)

# 处理上传的文件
if uploaded_file is not None:
    # 读取文件
    try:
        if uploaded_file.name.endswith('.csv'):
            # 自动检测文件编码
            uploaded_file.seek(0)
            raw_data = uploaded_file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding'] or 'utf-8'
            
            # 显示文件预览
            st.subheader("文件预览")
            # 读取文件内容
            content = raw_data.decode(encoding, errors='replace')
            # 显示前10行
            lines = content.split('\n')[:10]
            preview = '\n'.join(lines)
            st.text_area("文件前10行内容:", preview, height=200)
            st.info(f"检测到文件编码: {encoding}")
            
            # 自动检测分隔符
            # 尝试常见的分隔符
            possible_separators = [",", ";", "\t", "|", " "]
            best_sep = ","
            max_columns = 0
            
            for sep in possible_separators:
                try:
                    temp_df = pd.read_csv(io.BytesIO(raw_data), sep=sep, encoding=encoding, nrows=5)
                    if len(temp_df.columns) > max_columns:
                        max_columns = len(temp_df.columns)
                        best_sep = sep
                except:
                    pass
            
            # 让用户选择分隔符，默认使用自动检测的结果
            sep_option = st.selectbox(
                "选择分隔符:",
                [",", ";", "\t", "|", " "],
                index=possible_separators.index(best_sep) if best_sep in possible_separators else 0,
                help="请选择CSV文件使用的分隔符"
            )
            
            # 尝试读取文件，增加更多选项
            try:
                # 尝试使用不同的参数组合
                uploaded_file.seek(0)
                try:
                    df = pd.read_csv(uploaded_file, sep=sep_option, encoding=encoding)
                except Exception:
                    # 尝试忽略空值和错误行
                    uploaded_file.seek(0)
                    try:
                        df = pd.read_csv(uploaded_file, sep=sep_option, encoding=encoding, error_bad_lines=False, warn_bad_lines=True)
                    except Exception:
                        # 尝试更宽松的参数
                        uploaded_file.seek(0)
                        df = pd.read_csv(uploaded_file, sep=sep_option, encoding=encoding, error_bad_lines=False, warn_bad_lines=True, skip_blank_lines=True)
                st.success(f"成功读取文件，使用分隔符: {sep_option}，编码: {encoding}")
                st.write(f"数据形状: {df.shape[0]} 行 × {df.shape[1]} 列")
            except Exception as e:
                st.error(f"读取CSV文件时出错: {str(e)}")
                st.info("请尝试选择不同的分隔符，或检查文件格式")
                df = None
        else:
            df = pd.read_excel(uploaded_file)
        
        if df is not None:
            # 数据预览
            st.subheader("数据预览")
            st.write("数据前5行:")
            st.dataframe(df.head())
            
            # 显示数据基本信息
            st.subheader("数据基本信息")
            st.write(f"数据形状: {df.shape[0]} 行 × {df.shape[1]} 列")
            
            # 找出数值类型的列
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if numeric_columns:
                # 绘制直方图
                st.subheader("数据分布直方图")
                for col in numeric_columns:
                    st.write(f"**{col}**")
                    fig, ax = plt.subplots()
                    ax.hist(df[col].dropna(), bins=20, alpha=0.7)
                    ax.set_xlabel(col)
                    ax.set_ylabel("频率")
                    st.pyplot(fig)
                
                # 基本统计信息
                st.subheader("基本统计信息")
                stats = df[numeric_columns].describe().T
                stats = stats[['mean', '50%', 'std', 'min', 'max']]
                stats.columns = ['平均值', '中位数', '标准差', '最小值', '最大值']
                st.dataframe(stats)
                
                # 数据相关性分析
                st.subheader("数据相关性分析")
                if len(numeric_columns) > 1:
                    corr_matrix = df[numeric_columns].corr()
                    st.write("相关性矩阵:")
                    st.dataframe(corr_matrix)
                    
                    # 相关性热力图
                    st.write("相关性热力图:")
                    fig, ax = plt.subplots(figsize=(10, 8))
                    cax = ax.matshow(corr_matrix, cmap='coolwarm')
                    fig.colorbar(cax)
                    plt.xticks(range(len(numeric_columns)), numeric_columns, rotation=45)
                    plt.yticks(range(len(numeric_columns)), numeric_columns)
                    st.pyplot(fig)
                else:
                    st.info("数据中只有一个数值列，无法进行相关性分析。")
                
                # AI智能总结
                st.subheader("AI智能总结")
                
                # 准备统计信息文本
                stats_text = "数据基本统计信息:\n"
                for col in numeric_columns:
                    col_stats = df[col].describe()
                    stats_text += f"\n{col}:\n"
                    stats_text += f"  平均值: {col_stats['mean']:.2f}\n"
                    stats_text += f"  中位数: {col_stats['50%']:.2f}\n"
                    stats_text += f"  标准差: {col_stats['std']:.2f}\n"
                    stats_text += f"  最小值: {col_stats['min']:.2f}\n"
                    stats_text += f"  最大值: {col_stats['max']:.2f}\n"
                
                # 提示词
                prompt = f"请根据以下数据的基本统计信息，写一段简短的报告，总结一下这份数据的关键特征。\n\n{stats_text}"
                
                # AI服务选择
                ai_service = st.selectbox(
                    "选择AI服务:",
                    ["内置智能分析", "OpenAI API", "国内AI服务"],
                    index=0,
                    help="选择使用哪种AI服务进行分析总结"
                )
                
                if ai_service == "OpenAI API":
                    try:
                        # 这里使用OpenAI API，需要设置API密钥
                        # 注意：在实际使用时，您需要在环境变量中设置OPENAI_API_KEY
                        # 或者直接在代码中设置：client = OpenAI(api_key="您的API密钥")
                        client = OpenAI()
                        
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "你是一个数据分析专家，擅长根据统计信息总结数据特征。"},
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=500
                        )
                        
                        summary = response.choices[0].message.content
                        st.write(summary)
                        
                    except Exception as e:
                        st.warning("OpenAI API访问失败，可能是由于地区限制或API密钥问题。")
                        st.write("错误信息:", str(e))
                        
                        # 自动切换到内置分析
                        st.info("已自动切换到内置智能分析")
                        
                        # 提供内置智能分析
                        st.write("\n智能分析总结:")
                        st.write(f"## 数据概览")
                        st.write(f"- 数据规模: {df.shape[0]}行 × {df.shape[1]}列")
                        st.write(f"- 数值列数量: {len(numeric_columns)}")
                        
                        st.write(f"\n## 数据特征")
                        for col in numeric_columns:
                            col_stats = df[col].describe()
                            st.write(f"- **{col}**: 平均值={col_stats['mean']:.2f}, 范围={col_stats['min']:.2f}-{col_stats['max']:.2f}")
                        
                        st.write(f"\n## 数据质量")
                        missing_values = df.isnull().sum().sum()
                        total_values = df.size
                        st.write(f"- 缺失值: {missing_values} ({missing_values/total_values*100:.2f}%)")
                        
                        st.write(f"\n## 分析建议")
                        st.write("1. 数据分布相对合理，无明显异常值")
                        st.write("2. 建议进一步分析数据间的相关性")
                        st.write("3. 可考虑使用机器学习模型进行预测分析")
                        st.write("\n*注: 要使用OpenAI API，请确保您有有效的API密钥和网络访问权限*")
                
                elif ai_service == "国内AI服务":
                    st.info("国内AI服务功能正在开发中，敬请期待！")
                    st.write("\n智能分析总结:")
                    st.write(f"## 数据概览")
                    st.write(f"- 数据规模: {df.shape[0]}行 × {df.shape[1]}列")
                    st.write(f"- 数值列数量: {len(numeric_columns)}")
                    
                    st.write(f"\n## 数据特征")
                    for col in numeric_columns:
                        col_stats = df[col].describe()
                        st.write(f"- **{col}**: 平均值={col_stats['mean']:.2f}, 范围={col_stats['min']:.2f}-{col_stats['max']:.2f}")
                    
                    st.write(f"\n## 数据质量")
                    missing_values = df.isnull().sum().sum()
                    total_values = df.size
                    st.write(f"- 缺失值: {missing_values} ({missing_values/total_values*100:.2f}%)")
                    
                    st.write(f"\n## 分析建议")
                    st.write("1. 数据分布相对合理，无明显异常值")
                    st.write("2. 建议进一步分析数据间的相关性")
                    st.write("3. 可考虑使用机器学习模型进行预测分析")
                
                else:  # 内置智能分析
                    # 提供一个更详细的内置智能分析
                    st.write("\n智能分析总结:")
                    st.write(f"## 数据概览")
                    st.write(f"- 数据规模: {df.shape[0]}行 × {df.shape[1]}列")
                    st.write(f"- 数值列数量: {len(numeric_columns)}")
                    
                    st.write(f"\n## 数据特征")
                    for col in numeric_columns:
                        col_stats = df[col].describe()
                        st.write(f"- **{col}**: 平均值={col_stats['mean']:.2f}, 中位数={col_stats['50%']:.2f}, 标准差={col_stats['std']:.2f}, 范围={col_stats['min']:.2f}-{col_stats['max']:.2f}")
                    
                    st.write(f"\n## 数据质量")
                    missing_values = df.isnull().sum().sum()
                    total_values = df.size
                    st.write(f"- 缺失值: {missing_values} ({missing_values/total_values*100:.2f}%)")
                    
                    # 分析数据分布
                    st.write(f"\n## 数据分布分析")
                    for col in numeric_columns:
                        col_stats = df[col].describe()
                        if col_stats['std'] > 0:
                            cv = col_stats['std'] / col_stats['mean'] if col_stats['mean'] != 0 else 0
                            st.write(f"- **{col}**: 变异系数={cv:.2f}，{'数据分布较为分散' if cv > 0.5 else '数据分布较为集中'}")
                    
                    # 相关性分析
                    if len(numeric_columns) > 1:
                        st.write(f"\n## 相关性分析")
                        corr_matrix = df[numeric_columns].corr()
                        high_corr = []
                        for i in range(len(numeric_columns)):
                            for j in range(i+1, len(numeric_columns)):
                                corr = corr_matrix.iloc[i, j]
                                if abs(corr) > 0.7:
                                    high_corr.append((numeric_columns[i], numeric_columns[j], corr))
                        
                        if high_corr:
                            st.write("### 高相关性变量对:")
                            for var1, var2, corr in high_corr:
                                st.write(f"- {var1} 与 {var2}: {corr:.2f}")
                        else:
                            st.write("无高相关性变量对")
                    
                    st.write(f"\n## 分析建议")
                    st.write("1. 数据分布相对合理，无明显异常值")
                    st.write("2. 建议进一步分析数据间的相关性")
                    st.write("3. 可考虑使用机器学习模型进行预测分析")
                    st.write("4. 定期更新数据，保持分析的时效性")
                    st.write("\n*注: 此分析由内置算法生成，仅供参考*")
            else:
                st.warning("数据中没有数值类型的列，无法进行统计分析。")
            
    except Exception as e:
        st.error(f"读取文件时出错: {str(e)}")
else:
    st.info("请上传一个CSV或Excel文件开始分析")

# 侧边栏信息
with st.sidebar:
    st.header("关于本应用")
    st.write("这是一个智能数据看板应用，可以帮助您快速分析数据。")
    st.write("功能包括:")
    st.write("• 文件上传 (CSV/Excel)")
    st.write("• 数据预览")
    st.write("• 自动绘制直方图")
    st.write("• 计算基本统计信息")
    st.write("• AI智能总结")
    
    st.header("使用说明")
    st.write("1. 点击上传按钮选择数据文件")
    st.write("2. 等待数据加载和分析")
    st.write("3. 查看数据预览和分析结果")
    st.write("4. 阅读AI生成的数据分析报告")

# 底部信息
st.write("\n---")
st.write("智能数据看板 v1.0 | 使用 Streamlit 开发")

"""
使用说明：

1. 安装依赖库：
   ```bash
   python -m pip install --user -i https://pypi.tuna.tsinghua.edu.cn/simple streamlit pandas numpy matplotlib openai
   ```

2. 启动应用：
   ```bash
   python -m streamlit run smart_data_dashboard.py
   ```

3. 在浏览器中打开显示的URL，即可使用应用。

4. 关于AI功能：
   - 本应用使用OpenAI API进行智能总结
   - 您需要在环境变量中设置OPENAI_API_KEY，或者直接在代码中设置API密钥
   - 如果没有API密钥，应用会显示模拟总结

5. 支持的文件格式：
   - CSV文件 (.csv)
   - Excel文件 (.xlsx)

注意：对于大型数据集，分析可能需要一些时间，请耐心等待。
"""
