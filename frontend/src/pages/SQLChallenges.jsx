import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Database, 
  Sparkles, 
  Search, 
  AlertCircle, 
  Play, 
  Loader2, 
  Terminal, 
  Table, 
  Cpu, 
  Layers 
} from 'lucide-react';
import SearchBar from '../components/SearchBar';
import LoadingSpinner from '../components/LoadingSpinner';
import { challengeService } from '../services/challengeService';

const INITIAL_SQL_CHALLENGES = [
  {
    id: 'SQL-E01',
    title: 'Incorrect WHERE clause returns extra records',
    description: 'A SELECT query returns all rows from the orders table because the WHERE clause filtering for completed status is missing.',
    difficulty: 'Easy',
    technology: 'SQL',
    category: 'Query',
    timeEstimate: '10 mins',
    points: 100,
    tables: ['orders', 'customers'],
    expectedOutput: 'Query returns only the intended rows matching the filter condition.'
  },
  {
    id: 'SQL-E02',
    title: 'ORDER BY sorts incorrectly',
    description: 'Results are sorted in the wrong order because the ORDER BY uses the wrong field or missing direction.',
    difficulty: 'Easy',
    technology: 'SQL',
    category: 'Sorting',
    timeEstimate: '10 mins',
    points: 100,
    tables: ['products'],
    expectedOutput: 'Rows are ordered correctly by the requested column and sort direction.'
  },
  {
    id: 'SQL-E03',
    title: 'Missing PRIMARY KEY',
    description: 'A table has no PRIMARY KEY constraint, causing duplicate rows and unreliable joins.',
    difficulty: 'Easy',
    technology: 'SQL',
    category: 'Schema',
    timeEstimate: '10 mins',
    points: 100,
    tables: ['users'],
    expectedOutput: 'The table includes a valid PRIMARY KEY definition.'
  },
  {
    id: 'SQL-E04',
    title: 'Duplicate usernames allowed',
    description: 'The users table lacks a UNIQUE constraint on username, allowing duplicate accounts.',
    difficulty: 'Easy',
    technology: 'SQL',
    category: 'Constraints',
    timeEstimate: '10 mins',
    points: 100,
    tables: ['users'],
    expectedOutput: 'Username column is constrained to unique values.'
  },
  {
    id: 'SQL-M01',
    title: 'GROUP BY omits aggregate column',
    description: 'A report query fails because the SELECT list includes a non-aggregated column without a corresponding GROUP BY expression.',
    difficulty: 'Medium',
    technology: 'SQL',
    category: 'Aggregation',
    timeEstimate: '15 mins',
    points: 150,
    tables: ['sales', 'regions'],
    expectedOutput: 'Aggregate report returns grouped values for each region without SQL errors.'
  },
  {
    id: 'SQL-M02',
    title: 'JOIN duplicates rows unexpectedly',
    description: 'A multi-table join returns duplicate records because the join condition is too broad or the join type is incorrect.',
    difficulty: 'Medium',
    technology: 'SQL',
    category: 'Joins',
    timeEstimate: '15 mins',
    points: 150,
    tables: ['orders', 'customers', 'order_items'],
    expectedOutput: 'The query returns each matching record once with the expected relationship.'
  },
  {
    id: 'SQL-M03',
    title: 'HAVING used instead of WHERE',
    description: 'A filter on aggregated results is applied in the wrong clause, so the final output is incorrect.',
    difficulty: 'Medium',
    technology: 'SQL',
    category: 'Filtering',
    timeEstimate: '15 mins',
    points: 150,
    tables: ['sales'],
    expectedOutput: 'Where clause is applied before grouping.'
  },
  {
    id: 'SQL-H01',
    title: 'CTE recursive query infinite loop',
    description: 'A Common Table Expression lacks a base case termination condition.',
    difficulty: 'Hard',
    technology: 'SQL',
    category: 'Advanced CTE',
    timeEstimate: '25 mins',
    points: 250,
    tables: ['org_chart'],
    expectedOutput: 'Recursive CTE terminates correctly.'
  },
  {
    id: 'SQL-H02',
    title: 'Index hint prevents plan reuse',
    description: 'A query uses the wrong index hint and performs a full table scan even though a better index exists.',
    difficulty: 'Hard',
    technology: 'SQL',
    category: 'Performance',
    timeEstimate: '25 mins',
    points: 250,
    tables: ['events'],
    expectedOutput: 'The query uses the intended index strategy for efficient execution.'
  }
];

export default function SQLChallenges({ addToast }) {
  const [challenges, setChallenges] = useState(INITIAL_SQL_CHALLENGES);
  const [searchVal, setSearchVal] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('All');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [generating, setGenerating] = useState(false);
  const [genDifficulty, setGenDifficulty] = useState('Medium');

  const handleGenerateSQLChallenge = async () => {
    try {
      setGenerating(true);
      await new Promise(r => setTimeout(r, 1000));
      const newChal = {
        id: `sql-ai-${Date.now()}`,
        title: `AI SQL: ${genDifficulty} Multi-Table Query #${Math.floor(Math.random() * 900 + 100)}`,
        description: `Dynamically generated ${genDifficulty} SQL query challenge involving data aggregation, join optimization, and indexed constraints.`,
        difficulty: genDifficulty,
        technology: 'SQL',
        category: 'AI Generated Query',
        timeEstimate: genDifficulty === 'Easy' ? '10 mins' : genDifficulty === 'Medium' ? '15 mins' : '25 mins',
        points: genDifficulty === 'Easy' ? 100 : genDifficulty === 'Medium' ? 150 : 300,
        tables: ['analytics_events', 'session_data'],
        expectedOutput: 'Optimized SQL query returning expected schema columns without table scans.'
      };
      setChallenges(prev => [newChal, ...prev]);
      addToast(`Generated dynamic ${genDifficulty} SQL challenge!`, 'success');
    } catch (err) {
      addToast('Failed to generate SQL challenge.', 'error');
    } finally {
      setGenerating(false);
    }
  };

  const filteredChallenges = challenges.filter(c => {
    const matchesSearch = c.title.toLowerCase().includes(searchVal.toLowerCase()) ||
                          c.description.toLowerCase().includes(searchVal.toLowerCase());
    const matchesDifficulty = selectedDifficulty === 'All' || c.difficulty === selectedDifficulty;
    const matchesCategory = selectedCategory === 'All' || c.category === selectedCategory;
    return matchesSearch && matchesDifficulty && matchesCategory;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="badge badge-cyan">DATABASE LAB</span>
            <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">PostgreSQL • MySQL • SQLite</span>
          </div>
          <h1 className="font-heading font-extrabold text-2xl text-slate-800 dark:text-[#F0F2F4] flex items-center gap-2.5">
            <Database className="w-7 h-7 text-cyan-500" />
            <span>SQL Debugging & Query Optimization</span>
          </h1>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Master database indexing, JOIN optimization, CTEs, and query performance debugging.</p>
        </div>

        <SearchBar 
          value={searchVal}
          onChange={setSearchVal}
          onClear={() => setSearchVal('')}
          placeholder="Search SQL challenges..."
        />
      </div>

      {/* AI SQL Challenge Generator Banner */}
      <div className="glass-panel p-6 rounded-xl border border-cyan-500/30 bg-white dark:bg-[#15181B] relative overflow-hidden">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="p-3.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-500 dark:text-cyan-400">
              <Cpu className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="badge badge-emerald">AI SQL ENGINE</span>
                <span className="text-[10px] text-slate-500 dark:text-slate-400 font-medium">Auto-generate relational schema & query bugs</span>
              </div>
              <h2 className="font-heading font-bold text-lg text-slate-800 dark:text-[#F0F2F4]">Generate Custom SQL Challenge</h2>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
            {/* Difficulty Selector */}
            <div className="flex bg-slate-100 dark:bg-[#1B1F23] p-1 rounded-lg border border-slate-200 dark:border-[#292E33] text-xs font-semibold">
              {['Easy', 'Medium', 'Hard'].map((diff) => (
                <button
                  key={diff}
                  onClick={() => setGenDifficulty(diff)}
                  className={`px-3 py-1.5 rounded-md transition-colors ${
                    genDifficulty === diff 
                      ? diff === 'Easy' ? 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30' 
                        : diff === 'Medium' ? 'bg-amber-500/20 text-amber-600 dark:text-amber-400 border border-amber-500/30'
                        : 'bg-rose-500/20 text-rose-600 dark:text-rose-400 border border-rose-500/30'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                  }`}
                >
                  {diff}
                </button>
              ))}
            </div>

            <button
              onClick={handleGenerateSQLChallenge}
              disabled={generating}
              className="button-primary px-5 py-2 text-xs font-bold whitespace-nowrap"
            >
              {generating ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Generating SQL Task...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5 text-white" />
                  <span>Generate SQL Challenge</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Difficulty Filter Bar */}
      <div className="flex flex-wrap items-center gap-3 glass-panel p-4 rounded-xl border border-slate-200 dark:border-[#292E33]">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-1.5 mr-2">
          <Layers className="w-3.5 h-3.5 text-cyan-500" />
          <span>Difficulty:</span>
        </span>
        {['All', 'Easy', 'Medium', 'Hard'].map((d) => (
          <button
            key={d}
            onClick={() => setSelectedDifficulty(d)}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
              selectedDifficulty === d
                ? 'bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30'
                : 'bg-white dark:bg-[#1B1F23] text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 border border-slate-200 dark:border-[#292E33]'
            }`}
          >
            {d}
          </button>
        ))}
      </div>

      {/* Challenge Grid */}
      {filteredChallenges.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredChallenges.map((chal) => (
            <div key={chal.id} className="glass-panel rounded-xl p-6 flex flex-col justify-between hover:border-cyan-500/40 transition-all duration-200 relative group">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className={`badge ${
                    chal.difficulty === 'Easy' ? 'badge-emerald' : chal.difficulty === 'Medium' ? 'badge-amber' : 'badge-rose'
                  }`}>
                    {chal.difficulty}
                  </span>
                  <span className="badge badge-cyan">
                    {chal.category}
                  </span>
                </div>

                <div className="space-y-2">
                  <h3 className="font-heading font-bold text-base text-slate-800 dark:text-[#F0F2F4] group-hover:text-cyan-600 dark:group-hover:text-cyan-400 transition-colors">
                    {chal.title}
                  </h3>
                  <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                    {chal.description}
                  </p>
                </div>

                {/* Schema Tables Involved */}
                <div className="flex items-center gap-2 pt-1">
                  <Table className="w-3.5 h-3.5 text-slate-500" />
                  <span className="text-[11px] text-slate-600 dark:text-slate-400 font-mono">
                    Tables: {chal.tables.join(', ')}
                  </span>
                </div>
              </div>

              <div className="border-t border-slate-200 dark:border-[#292E33] pt-4 mt-5 flex items-center justify-between">
                <div className="text-[10px] text-slate-500 font-bold space-y-0.5">
                  <p className="uppercase">EST. TIME: <span className="text-slate-700 dark:text-slate-300">{chal.timeEstimate}</span></p>
                  <p className="uppercase">XP REWARD: <span className="text-cyan-600 dark:text-cyan-400">{chal.points} XP</span></p>
                </div>

                <Link 
                  to={`/challenge/${chal.id}`}
                  className="button-primary px-4 py-2 text-xs"
                >
                  <Terminal className="w-3.5 h-3.5" />
                  <span>Launch SQL Lab</span>
                </Link>

              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="glass-panel rounded-xl p-12 text-center max-w-lg mx-auto text-slate-600 dark:text-slate-400">
          <AlertCircle className="w-10 h-10 text-cyan-500 mx-auto mb-3" />
          <h3 className="font-heading font-bold text-slate-800 dark:text-[#F0F2F4]">No SQL Challenges Found</h3>
          <p className="text-xs text-slate-500 mt-1">Try clearing your filters or generating a new SQL challenge using AI.</p>
        </div>
      )}
    </div>
  );
}
