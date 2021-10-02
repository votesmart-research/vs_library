
class Incumbents:

    statement = \
        """
        SELECT DISTINCT ON (candidate.candidate_id)
        candidate.candidate_id,
        candidate.firstname,
        candidate.nickname,
        candidate.middlename,
        candidate.lastname,
        candidate.suffix,
        office.name as office,
        state.name as state,
        districtname.name as district,
        party.name as party

        FROM office_candidate
        JOIN candidate USING (candidate_id)
        JOIN office_candidate_party USING (office_candidate_id)

        LEFT JOIN office USING (office_id)
        LEFT JOIN state ON office_candidate.state_id = state.state_id
        LEFT JOIN districtname USING (districtname_id)
        LEFT JOIN party USING (party_id)
        """

    def __init__(self, active_years, office_ids, office_types, states):

        self.__conditions = {'year': int(max(active_years)),
                             'start_date': f'01-01-{min(active_years)}',
                             'end_date': f'12-31-{max(active_years)}'}

        self.__enum_office_ids = {f"office_id_{k}": v for k, v in enumerate(office_ids)} if office_ids else {"office_id_0": -1}
        self.__enum_office_types = {f"office_type_{k}": str(v) for k, v in enumerate(office_types)} if office_types else {"office_type_0": ''}
        self.__enum_states = {f"state_{k}": v for k, v in enumerate(states)}

        self.__conditions.update(self.__enum_office_ids)
        self.__conditions.update(self.__enum_office_types)
        self.__conditions.update(self.__enum_states)

    def by_congstatus(self):

        statement = \
            """
            JOIN congstatus_candidate USING (office_candidate_id)
            JOIN congstatus USING (congstatus_id)

            WHERE congstatus.statusdate BETWEEN :start_date AND :end_date
            AND office_candidate.state_id IN ({states})
            AND (office.office_id IN ({office_ids})
                 OR office.officetype_id IN ({office_types}))
            """.format(states=','.join([f':{k}' for k in self.__enum_states.keys()]),
                 office_types=','.join([f':{k}' for k in self.__enum_office_types.keys()]),
                   office_ids=','.join([f':{k}' for k in self.__enum_office_ids.keys()]))

        return Incumbents.statement + statement, self.__conditions

    def by_electdates(self):

        statement = \
            """
            WHERE (
                (:year BETWEEN EXTRACT(year FROM to_date(firstelect, 'mm/dd/yyyy'))
                              AND EXTRACT(year FROM to_date(lastelect, 'mm/dd/yyyy'))            
                AND EXTRACT(year FROM to_date(firstelect, 'mm/dd/yyyy')) > 1000)
            OR
                (:year BETWEEN EXTRACT(year FROM to_date(firstelect,'mm/yyyy'))
                             AND EXTRACT(year FROM to_date(lastelect, 'mm/yyyy'))
                AND EXTRACT(year FROM to_date(firstelect, 'mm/yyyy')) > 1000)
            OR
                (:year BETWEEN EXTRACT(year FROM to_date(firstelect,'yyyy'))
                             AND EXTRACT(year FROM to_date(lastelect, 'yyyy'))
                AND EXTRACT(year FROM to_date(firstelect, 'yyyy')) > 1000)
            OR
                (:year BETWEEN EXTRACT(year FROM to_date(firstelect,'mm/dd/yyyy'))
                             AND EXTRACT(year FROM CASE WHEN lastelect = '' THEN now() END)
                AND EXTRACT(year FROM to_date(firstelect, 'mm/dd/yyyy')) > 1000)
            OR
                (:year BETWEEN EXTRACT(year FROM to_date(firstelect,'mm/yyyy'))
                             AND EXTRACT(year FROM CASE WHEN lastelect = '' THEN now() END)
                AND EXTRACT(year FROM to_date(firstelect, 'mm/yyyy')) > 1000)
            OR
                (:year BETWEEN EXTRACT(year FROM to_date(firstelect,'yyyy'))
                             AND EXTRACT(year FROM CASE WHEN lastelect = '' THEN now() END)
                AND EXTRACT(year FROM to_date(firstelect, 'yyyy')) > 1000)
                )
            AND office_candidate.state_id IN ({states})
            AND (office.office_id IN ({office_ids})
                 OR office.officetype_id IN ({office_types}))
            """.format(office_ids=','.join([f':{k}' for k in self.__enum_office_ids.keys()]),
                     office_types=','.join([f':{k}' for k in self.__enum_office_types.keys()]),
                           states=','.join([f':{k}' for k in self.__enum_states.keys()]))

        return Incumbents.statement + statement, self.__conditions


class ElectionCandidates:

    statement = \
        """SELECT DISTINCT ON (candidate.candidate_id)
            candidate.candidate_id,
            candidate.firstname,
            candidate.nickname,
            candidate.middlename,
            candidate.lastname,
            candidate.suffix,
            office.name as office,
            state.name as state,
            districtname.name as district,
            party.name as party

            FROM election_candidate
            JOIN candidate USING (candidate_id)
            JOIN election USING (election_id)
            JOIN electionstage_candidate USING (election_candidate_id)
            JOIN election_electionstage USING (election_electionstage_id)

            LEFT JOIN office USING (office_id)
            LEFT JOIN state ON election.state_id = state.state_id
            LEFT JOIN districtname USING (districtname_id)
            LEFT JOIN electionstage_candidate_party USING (electionstage_candidate_id)
            LEFT JOIN party ON electionstage_candidate_party.party_id = party.party_id
            """

    def __init__(self, election_years, election_stages, office_ids, office_types, states):

        self.__enum_election_years = {f"election_year_{k}": int(v) for k, v in enumerate(election_years)}
        self.__enum_election_stages = {f"election_stage_{k}": v for k, v in enumerate(election_stages)}
        self.__enum_office_ids = {f"office_id_{k}": v for k, v in enumerate(office_ids)} if office_ids else {'office_id_0':-1}
        self.__enum_office_types = {f"office_type_{k}": str(v) for k, v in enumerate(office_types)} if office_types else {'office_type_0':''}
        self.__enum_states = {f"state_{k}": v for k, v in enumerate(states)}

        self.__conditions = {**self.__enum_election_years, **self.__enum_election_stages, **self.__enum_office_ids,
                             **self.__enum_office_types, **self.__enum_states}

    def by_yoss(self):

        statement = \
            """WHERE election.electionyear IN ({election_years})
                AND election_electionstage.electionstage_id IN ({election_stages})
                AND (office.office_id IN ({office_ids})
                    OR office.officetype_id IN ({office_types}))
                AND election_candidate.state_id IN ({states})
            """.format(election_years=','.join([f':{k}' for k in self.__enum_election_years.keys()]),
                      election_stages=','.join([f':{k}' for k in self.__enum_election_stages.keys()]),
                           office_ids=','.join([f':{k}' for k in self.__enum_office_ids.keys()]),
                         office_types=','.join([f':{k}' for k in self.__enum_office_types.keys()]),
                               states=','.join([f':{k}' for k in self.__enum_states.keys()]))

        return ElectionCandidates.statement + statement, self.__conditions
