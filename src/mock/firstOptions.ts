import {
  FaChartPie,
  FaPiggyBank,
  FaFileAlt,
  FaBalanceScale,
  FaInfoCircle,
  FaChartLine,
} from 'react-icons/fa';

interface Option {
  key: string;
  title: string;
  description: string;
  icon: React.ElementType;
  bgColor: string;
}

const firstOptions: Option[] = [
  {
    key: 'project_analysis',
    title: 'Analyse My Data',
    description: 'Get insights from your dataset quickly',
    icon: FaChartPie,
    bgColor: 'green.400',
  },
  {
    key: 'cost_optimization',
    title: 'Let`s Optimize Costs',
    description: 'Find ways to reduce expenses efficiently',
    icon: FaPiggyBank,
    bgColor: 'blue.400',
  },
  {
    key: 'executive_report',
    title: 'Prepare Executive Report',
    description: 'Create reports for your managers',
    icon: FaFileAlt,
    bgColor: 'orange.400',
  },
  {
    key: 'default',
    title: 'Compare with Industry',
    description: 'Benchmark your metrics against others',
    icon: FaBalanceScale,
    bgColor: 'purple.400',
  },
  {
    key: 'default',
    title: 'Explain a Metric',
    description: 'Understand what the numbers mean',
    icon: FaInfoCircle,
    bgColor: 'teal.400',
  },
  {
    key: 'default',
    title: 'Predict Future Trends',
    description: 'Use AI to forecast upcoming patterns',
    icon: FaChartLine,
    bgColor: 'pink.400',
  },
];

export default firstOptions;
