const fs = require('fs');

let content = fs.readFileSync('frontend/src/App.jsx', 'utf8');

const oldPlotParams = `  const [plotParams, setPlotParams] = useState({
    freq_min: 2.7,
    freq_max: 4.1,
    reqS11Val: -10,
    reqS21Val: -14,
    n_avg: 20,
    u_bound_s21: 2,
    l_bound_s21: 2,
    u_bound_npd: 2,
    l_bound_npd: 2,
  });`;

const newPlotParams = `  const [plotParams, setPlotParams] = useState({
    freq_min: 2.7,
    freq_max: 4.1,
    reqS11Val: -10,
    reqS21Val: -14,
    n_avg: 20,
    u_bound_s21: 15,
    l_bound_s21: 5,
    u_bound_npd: -100,
    l_bound_npd: -130,
  });

  useEffect(() => {
    if (testType === 1) {
      setPlotParams(prev => ({
        ...prev,
        freq_min: 2.7,
        freq_max: 4.1,
        u_bound_s21: 15,
        l_bound_s21: 5,
        u_bound_npd: -100,
        l_bound_npd: -130,
      }));
    } else {
      setPlotParams(prev => ({
        ...prev,
        freq_min: 1.5,
        freq_max: 3.0,
        u_bound_s21: 15,
        l_bound_s21: 5,
        u_bound_npd: -135,
        l_bound_npd: -168,
      }));
    }
  }, [testType]);`;

content = content.replace(oldPlotParams, newPlotParams);
fs.writeFileSync('frontend/src/App.jsx', content);
