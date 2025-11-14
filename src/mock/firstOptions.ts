import {
  FaChartPie,
  FaPiggyBank,
  FaBalanceScale,
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
    key: 'sales',
    title: 'SLM Sales Assistant',
    description: 'Get help with your sales strategy and execution',
    icon: FaBalanceScale,
    bgColor: 'purple.400',
  },

];

export default firstOptions;
