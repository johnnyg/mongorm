
class Q(object):
	def __init__( self, _query=None, **search ):
		if _query is None:
			if 'pk' in search:
				search['id'] = search['pk']
				del search['pk']
			
			self.query = search
		else:
			self.query = _query
	
	def toMongo( self, document, forUpdate=False ):
		newSearch = {}
		for (name, value) in self.query.iteritems( ):
			if name in ['$or', '$and']:
				# mongodb logic operator - value is a list of Qs
				newSearch[name] = [ value.toMongo( document ) for value in value ]
				continue
			
			fieldName = name

			comparison = None
			if '__' in fieldName:
				chunks = fieldName.split( '__' )
				fieldName = chunks[0]

				comparison = chunks[-1]

				if comparison in ['gt', 'lt', 'lte', 'gte']:
					dereferences = chunks[:-1]
				else:
					# not a comparison operator
					dereferences = chunks
					comparison = None

			field = document._fields[fieldName]
			if not forUpdate:
				searchValue = field.toQuery( value )
			else:
				searchValue = field.fromPython( value )

			if comparison is not None:
				newSearch[field.dbField] = { '$'+comparison: searchValue }
			else:
				if isinstance(searchValue, dict):
					if not forUpdate:
						for name,value in searchValue.iteritems( ):
							newSearch[field.dbField + '.' + name] = value
					else:
						newSearch[field.dbField] = searchValue
				else:
					newSearch[field.dbField] = searchValue

		return newSearch
	
	def __or__( self, other ):
		if len(self.query) == 0: return other
		if len(other.query) == 0: return self
				
		newQuery = { '$or': [ self, other ] }
		return Q( _query=newQuery )
	
	def __and__( self, other ):
		if len(self.query) == 0: return other
		if len(other.query) == 0: return self
		
		newQuery = { '$and': [ self, other ] }
		return Q( _query=newQuery )