import {
  FaApple,
  FaAndroid,
  FaReact,
  FaNode,
  FaPython,
  FaJava,
} from 'react-icons/fa';

interface Option {
  title: string;
  description: string;
  icon: React.ElementType;
  bgColor: string;
}

const firstOptions: Option[] = [
  {
    title: 'Analyse My Data',
    description: 'Get insights from your dataset quickly',
    icon: FaApple,
    bgColor: 'green.400',
  },
  {
    title: 'Let`s Optimize Costs',
    description: 'Find ways to reduce expenses efficiently',
    icon: FaAndroid,
    bgColor: 'blue.400',
  },
  {
    title: 'Prepare Executive Report',
    description: 'Create reports for your managers',
    icon: FaReact,
    bgColor: 'orange.400',
  },
  {
    title: 'Compare with Industry',
    description: 'Benchmark your metrics against others',
    icon: FaNode,
    bgColor: 'purple.400',
  },
  {
    title: 'Explain a Metric',
    description: 'Understand what the numbers mean',
    icon: FaPython,
    bgColor: 'teal.400',
  },
  {
    title: 'Predict Future Trends',
    description: 'Use AI to forecast upcoming patterns',
    icon: FaJava,
    bgColor: 'pink.400',
  },
];

export default firstOptions;
